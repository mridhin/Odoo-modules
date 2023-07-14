from odoo import api, models, fields, _
from odoo.exceptions import UserError
from datetime import datetime
import requests


class GitlabConnector(models.Model):
    _name = 'gitlab.connector'
    _description = "Gitlab Connector"

    name = fields.Char(string="Name")
    token = fields.Char(string="Token")
    url = fields.Char(string="URL")
    company_id = fields.Many2one("res.company", string="Company")
    states_prefix = fields.Char(string="Status Prefix",default="ERP DEV")

    def cron_import_gitlab_data(self):
        gitlab_records = self.sudo().search([])
        for rec in gitlab_records:
            rec.import_gitlab_project_data()
            rec.import_project_member_data()
            rec.import_project_labels()
            rec.import_project_milestones_data()
            rec.import_project_issue_data()

    def cron_update_issue(self):
        gitlab_records = self.sudo().search([])
        for rec in gitlab_records:
            rec.import_project_issue_data(update=True)

    def import_gitlab_project_data(self):
        url = self.url + "/api/v4/projects"
        payload = {}
        headers = {
            'PRIVATE-TOKEN': self.token
        }
        data = []
        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data.append(response.json())
            if response.links and response.links.get('next'):
                next_url = response.links['next'].get('url')
                while (next_url):
                    next_response = requests.request("GET", next_url, headers=headers, data=payload)
                    if next_response.status_code == 200:
                        data.append(next_response.json())
                    if next_response.links:
                        next_url = next_response.links['next'].get('url')
                    next_url = ""
        except:
            raise UserError(_('Please Check Your Connection'))
        # if response.status_code == 200:
            # response_data = response.json()
        project_obj = self.env['project.project'].sudo()
        for response_data in data:
            if len(data) == 1:
                response_data = data
            for rec in response_data:
                project = project_obj.search([('gitlab_id','=',str(rec.get('id')))])
                if not project:
                    vals = {
                        'name': rec.get('name') or '',
                        'gitlab_id': rec.get('id') or '',
                        'is_gitlab': True,
                    }
                    project_obj.create(vals)
        return {
            'effect': {
                'fadeout': 'slow',
                'message': "Import Project Process Completed",
                'type': 'rainbow_man',
            }
        }

    def update_gitlab_issue_webhook(self,data):
        task_obj = self.env['project.task'].sudo()
        project_obj = self.env['project.project'].sudo()
        users_obj = self.env['res.users'].sudo()
        project_tags_obj = self.env['project.tags'].sudo()
        project_milestone_obj = self.env['project.milestone'].sudo()
        milestone = False
        rec = data['object_attributes']
        task = task_obj.search([('gitlab_issue_id', '=', str(rec.get('id')))])
        project = project_obj.search([('gitlab_id', '=', str(rec.get('project_id')))])
        if rec.get('milestone'):
            milestone = project_milestone_obj.search([('gitlab_id', '=', str(rec['milestone'].get('id')))])
        labels = rec.get('labels') if rec.get('labels') else []
        member_list = []
        labels_list = []
        for label in labels:
            tag = project_tags_obj.search([('name', '=', label.get('title'))])
            if tag:
                labels_list.append(tag.id)
            else:
                vals = {
                    'name': label.get('title'),
                    'gitlab_label_id': rec.get('id'),
                }
                tag = project_tags_obj.create(vals)
                labels_list.append(tag.id)
        member = users_obj.search([('gitlab_member_id', '=', str(rec.get('assignee_id')))])
        if member:
            member_list.append(member.id)
        vals = {
            'name': rec.get('title') or '',
            'description': rec.get('description'),
            'project_id': project.id if project else False,
            'due_date': rec.get('due_date'),
            'user_ids': [(6, 0, member_list)],
            'tag_ids': [(6, 0, labels_list)],
            'milestone_id': milestone.id if milestone else False,
            'estimate_time': rec.get('human_time_estimate') or "",
        }
        if task:
            task.write(vals)
        # if not task:
        #     vals.update({
        #         'gitlab_issue_id': rec.get('id'),
        #     })
        #     task_obj.create(vals)

    def import_project_issue_data(self,update=False):
        projects = self.env['project.project'].sudo().search([('is_gitlab', '=', True)])
        task_obj = self.env['project.task'].sudo()
        project_obj = self.env['project.project'].sudo()
        users_obj = self.env['res.users'].sudo()
        project_tags_obj = self.env['project.tags'].sudo()
        project_milestone_obj = self.env['project.milestone'].sudo()
        task_type_obj = self.env['project.task.type'].sudo()
        milestone = False
        state_id = False
        for project in projects:
            url = self.url + "/api/v4/projects/" + project.gitlab_id + "/issues?per_page=100&pagination=keyset"
            payload = {}
            headers = {
                'PRIVATE-TOKEN': self.token
            }
            data = []
            try:
                response = requests.request("GET", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data.append(response.json())
                if response.links and response.links.get('next'):
                    next_url = response.links['next'].get('url')
                    while (next_url):
                        next_response = requests.request("GET", next_url, headers=headers, data=payload)
                        if next_response.status_code == 200:
                            data.append(next_response.json())
                        if next_response.links and next_response.links.get('next'):
                            next_url = next_response.links['next'].get('url')
                        next_url = ""
            except:
                raise UserError(_('Please Check Your Connection'))
            # if response.status_code == 200:
            #     response_data = response.json()
            for response_data in data:
                if len(data) == 1:
                    response_data = data[0]
                for rec in response_data:
                    task = task_obj.search([('gitlab_issue_id','=',str(rec.get('id')))])
                    project = project_obj.search([('gitlab_id','=',str(rec.get('project_id')))])
                    if rec.get('milestone'):
                        milestone = project_milestone_obj.search([('gitlab_id','=',str(rec['milestone'].get('id')))])
                    assignees = rec.get('assignees')
                    labels = rec.get('labels')
                    if len(labels) > 0:
                        state_id = task_type_obj.search([('name','=',labels[-1])])
                    member_list = []
                    labels_list = []
                    for label in labels:
                        tag = project_tags_obj.search([('name','=',label)])
                        if tag:
                            labels_list.append(tag.id)
                    for assignee in assignees:
                        member = users_obj.search([('gitlab_member_id','=',str(assignee.get('id')))])
                        if member:
                            member_list.append(member.id)
                    if not task:
                        vals = {
                            'name': rec.get('title') or '',
                            'gitlab_issue_id': rec.get('id'),
                            'description': rec.get('description'),
                            'project_id': project.id if project else False,
                            'due_date': rec.get('due_date'),
                            'user_ids': [(6, 0, member_list)],
                            'tag_ids': [(6, 0, labels_list)],
                            'milestone_id': milestone.id if milestone else False,
                            'estimate_time': rec['time_stats'].get('human_time_estimate'),
                            'stage_id': state_id.id if state_id else False,
                        }
                        task_obj.create(vals)
                    if task and update:
                        vals = {
                            'name': rec.get('title') or '',
                            'description': rec.get('description'),
                            'project_id': project.id if project else False,
                            'due_date': rec.get('due_date'),
                            'user_ids': [(6, 0, member_list)],
                            'tag_ids': [(6, 0, labels_list)],
                            'milestone_id': milestone.id if milestone else False,
                            'estimate_time': rec['time_stats'].get('human_time_estimate'),
                        }
                        task.write(vals)

        return {
            'effect': {
                'fadeout': 'slow',
                'message': "Import Project Issue Process Completed",
                'type': 'rainbow_man',
            }
        }

    def import_project_member_data(self):
        projects = self.env['project.project'].sudo().search([('is_gitlab','=',True)])
        users_obj = self.env['res.users'].sudo()
        for project in projects:
            url = self.url + "/api/v4/projects/" + project.gitlab_id + "/members/all"
            payload = {}
            headers = {
                'PRIVATE-TOKEN': self.token
            }
            try:
                response = requests.request("GET", url, headers=headers, data=payload)
            except:
                raise UserError(_('Please Check Your Connection'))
            if response.status_code == 200:
                response_data = response.json()
                for rec in response_data:
                    member = users_obj.search([('gitlab_member_id','=',str(rec.get('id')))])
                    if not member:
                        vals = {
                            'gitlab_member_id': rec.get('id'),
                            'name': rec.get('name') or "",
                            'login': rec.get('username') or "",
                            'gitlab_username': rec.get('username') or "",
                        }
                        users_obj.create(vals)
        return {
            'effect': {
                'fadeout': 'slow',
                'message': "Import Project Member Process Completed",
                'type': 'rainbow_man',
            }
        }

    def import_ticket_status(self):
        projects = self.env['project.project'].sudo().search([('is_gitlab', '=', True)])
        project_state = self.env['project.task.type'].sudo()
        for project in projects:
            url = self.url + "/api/v4/projects/" + project.gitlab_id + "/labels?pagination=keyset&order_by=id&sort=asc"
            payload = {}
            headers = {
                'PRIVATE-TOKEN': self.token
            }
            data = []
            try:
                response = requests.request("GET", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data.append(response.json())
                if response.links and response.links.get('next'):
                    next_url = response.links['next'].get('url')
                    while (next_url):
                        next_response = requests.request("GET", next_url, headers=headers, data=payload)
                        if next_response.status_code == 200:
                            data.append(next_response.json())
                        if next_response.links:
                            next_url = next_response.links['next'].get('url')
                        next_url = ""
            except:
                raise UserError(_('Please Check Your Connection'))
            for response_data in data:
                for rec in response_data:
                    if rec.get('name').startswith(self.states_prefix):
                        state = project_state.search([('name','=',str(rec.get('name')))])
                        if not state:
                            vals = {
                                'name': rec.get('name'),
                                'gitlab_id': rec.get('id'),
                                'project_ids': [(6,0,projects.ids)]
                            }
                            project_state.create(vals)
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': "Import Ticket Status Process Completed",
                    'type': 'rainbow_man',
                }
            }

    def import_project_labels(self):
        projects = self.env['project.project'].sudo().search([('is_gitlab', '=', True)])
        project_tag_obj = self.env['project.tags'].sudo()
        for project in projects:
            url = self.url + "/api/v4/projects/" + project.gitlab_id + "/labels?pagination=keyset&order_by=id&sort=asc"
            payload = {}
            headers = {
                'PRIVATE-TOKEN': self.token
            }
            data = []
            try:
                response = requests.request("GET", url, headers=headers, data=payload)
                if response.status_code == 200:
                    data.append(response.json())
                if response.links and response.links.get('next'):
                    next_url = response.links['next'].get('url')
                    while(next_url):
                        next_response = requests.request("GET", next_url, headers=headers, data=payload)
                        if next_response.status_code == 200:
                            data.append(next_response.json())
                        if next_response.links:
                            next_url = next_response.links['next'].get('url')
                        next_url = ""
            except:
                if response.status_code != 200 or next_response.status_code != 200:
                    raise UserError(_('Please Check Your Connection'))
            # if response.status_code == 200:
            #     data.append(response.json())
            for response_data in data:
                for rec in response_data:
                    # tag = project_tag_obj.search([('gitlab_label_id', '=', str(rec.get('id')))])
                    tag = project_tag_obj.search([('name', '=', rec.get('name'))])
                    if not tag:
                        vals = {
                            'name': rec.get('name'),
                            'gitlab_label_id': rec.get('id'),
                        }
                        project_tag_obj.create(vals)
        return {
            'effect': {
                'fadeout': 'slow',
                'message': "Import Project Labels Process Completed",
                'type': 'rainbow_man',
            }
        }

    def import_project_milestones_data(self):
        projects = self.env['project.project'].sudo().search([('is_gitlab', '=', True)])
        project_milestone_obj = self.env['project.milestone'].sudo()
        for project in projects:
            url = "https://git.awbni.com/api/v4/projects/" + project.gitlab_id + "/milestones"
            payload = {}
            headers = {
                'PRIVATE-TOKEN': self.token
            }
            try:
                response = requests.request("GET", url, headers=headers, data=payload)
            except:
                raise UserError(_('Please Check Your Connection'))
            if response.status_code == 200:
                response_data = response.json()
                for rec in response_data:
                    milestone = project_milestone_obj.search([('gitlab_id', '=', str(rec.get('id')))])
                    due_date = rec.get('due_date')
                    if not milestone:
                        vals = {
                            'name': rec.get('title'),
                            'project_id': project.id,
                            'gitlab_id': rec.get('id'),
                        }
                        if due_date:
                            due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
                            vals.update({
                                'deadline': due_date
                            })
                        project_milestone_obj.create(vals)

        return {
            'effect': {
                'fadeout': 'slow',
                'message': "Import Project Milestones Process Completed",
                'type': 'rainbow_man',
            }
        }

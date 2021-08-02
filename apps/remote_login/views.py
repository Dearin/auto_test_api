from django.views.generic import View
from libs.tool import json_response
from libs.parser import JsonParser, Argument
from remote_login.models import RemoteHost


class HanleRemoteHost(View):
	def post(self, request):
		# print(request.body)
		form, error = JsonParser(
			Argument('host', help='请输入ip'),
		).parse(request.body)
		print(form, error)
		if error is None:
			if RemoteHost.objects.filter(host=form.host).exists():
				return json_response(error=f'【{form.host}】已存在')
			RemoteHost.objects.create(host=form.host)
		return json_response(error=error)

	def get(self, request):
		remote_hosts = RemoteHost.objects.all()
		return json_response(remote_hosts)

	def delete(self, request):
		RemoteHost.objects.get(host=str(request.body, encoding='utf-8')).delete()
		return json_response(error='')


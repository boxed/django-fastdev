from django import forms


class IgnoredForm(forms.Form):
	my_field = forms.CharField()
	
	def clean_nonexistent_field(self):
		pass

from django import forms
from .models import Image

from urllib import request
from django.core.files.base import ContentFile
from django.utils.text import slugify


class ImageCreateForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['title', 'url', 'description']
        widgets = {'url': forms.HiddenInput, }

    def save(self, force_insert=False, force_update=False, commit=True):
        image = super(ImageCreateForm, self).save(commit=False)
        image_url = self.cleaned_data['url']
        image_name = '{}.{}'.format(
            slugify(image.title, allow_unicode=True),
            image_url.rsplit('.', 1)[1].lower()
        )
        # Скачиваем изображение по указанному адресу
        response = request.urlopen(image_url)
        # Download image
        image.image.save(
            image_name,
            ContentFile(response.read()),
            save=False
        )
        if commit:
            # Save to databse
            image.save()
        return image


    def clean_url(self):
        url = self.cleaned_data['url']
        valid_extensions = ['jpg', 'jpeg']
        extension = url.rsplit('.', 1)[1].lower()
        if extension not in valid_extensions:
            raise forms.ValidationError('The given URL does not match valid image extension')
        return url

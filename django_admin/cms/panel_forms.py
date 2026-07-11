from django import forms
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from django.utils.text import slugify
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import (
    Page, News, Document, DocumentSection, MenuItem, HomePage, HomeQuickLink,
    HomeBlock, Banner, Gallery, GalleryImage, ContentBlock, ContentTable,
    EducationalProgram, AdmissionYear, ProgramDocument,
)
from .embed_utils import content_for_editor, normalize_content_embeds
from .security_utils import sanitize_html


def _clean_rich_html(value):
    return normalize_content_embeds(sanitize_html(value or ''))


class SlugFormMixin:
    """Автогенерация и проверка slug."""

    def clean_slug(self):
        slug = (self.cleaned_data.get('slug') or '').strip()
        title = (self.cleaned_data.get('title') or '').strip()
        if not slug and title:
            slug = slugify(title, allow_unicode=True)
        if not slug:
            raise forms.ValidationError(
                'Укажите ссылку (URL) страницы или заполните заголовок — slug создастся автоматически.'
            )
        model = self._meta.model
        qs = model.objects.filter(slug=slug)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f'Страница с URL «{slug}» уже существует. Выберите другой.')
        return slug


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput, forms.RadioSelect)):
                widget.attrs.setdefault('class', 'form-check-input')
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault('class', 'form-select')
            elif isinstance(widget, forms.Textarea):
                widget.attrs.setdefault('class', 'form-control')
            elif not isinstance(widget, CKEditorUploadingWidget):
                widget.attrs.setdefault('class', 'form-control')


class PageForm(SlugFormMixin, StyledModelForm):
    class Meta:
        model = Page
        fields = [
            'title', 'slug', 'content',
            'is_published', 'show_in_menu', 'parent', 'order',
            'description', 'meta_title', 'meta_description', 'meta_keywords',
        ]
        widgets = {
            'content': CKEditorUploadingWidget(),
            'description': forms.Textarea(attrs={'rows': 2}),
            'meta_description': forms.Textarea(attrs={'rows': 2}),
            'slug': forms.TextInput(attrs={'placeholder': 'создаётся из заголовка'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        self.fields['parent'].required = False
        self.fields['order'].required = False
        if not self.instance.pk:
            self.fields['order'].initial = 0
        if self.instance.pk and self.instance.content:
            self.initial.setdefault(
                'content',
                content_for_editor(self.instance.content),
            )

    def clean_content(self):
        return _clean_rich_html(self.cleaned_data.get('content', ''))


class ContentTableForm(SlugFormMixin, StyledModelForm):
    class Meta:
        model = ContentTable
        fields = ['title', 'slug', 'content']
        widgets = {
            'content': CKEditorUploadingWidget(),
            'slug': forms.TextInput(attrs={'placeholder': 'создаётся из названия'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False

    def clean_content(self):
        return _clean_rich_html(self.cleaned_data.get('content', ''))


class FooterForm(StyledModelForm):
    class Meta:
        model = HomePage
        fields = [
            'footer_tagline', 'footer_copyright',
            'contacts_address', 'contacts_phone', 'contacts_email',
            'site_vk', 'site_telegram',
        ]


class NewsForm(SlugFormMixin, StyledModelForm):
    class Meta:
        model = News
        fields = ['title', 'slug', 'excerpt', 'content', 'image', 'tag', 'is_published']
        widgets = {
            'content': CKEditorUploadingWidget(),
            'excerpt': forms.Textarea(attrs={'rows': 3}),
            'slug': forms.TextInput(attrs={'placeholder': 'создаётся из заголовка'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False

    def clean_content(self):
        return _clean_rich_html(self.cleaned_data.get('content', ''))


class DocumentForm(StyledModelForm):
    class Meta:
        model = Document
        fields = [
            'page', 'category', 'title', 'description',
            'file', 'external_url', 'order', 'is_active',
        ]
        widgets = {'description': forms.Textarea(attrs={'rows': 2})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['page'].required = False
        self.fields['order'].required = False
        if not self.instance.pk:
            self.fields['order'].initial = 0


class PanelUserForm(StyledModelForm):
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        required=False,
        help_text='Оставьте пустым, чтобы не менять пароль',
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active']

    def __init__(self, *args, **kwargs):
        self._request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)
        if self._request_user and not self._request_user.is_superuser:
            self.fields['is_staff'].disabled = True

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        elif not user.pk:
            user.set_password(User.objects.make_random_password())
        if commit:
            user.save()
        return user


class DocumentSectionForm(StyledModelForm):
    class Meta:
        model = DocumentSection
        fields = ['page', 'category', 'title', 'order', 'is_active']


class MenuItemForm(StyledModelForm):
    class Meta:
        model = MenuItem
        fields = ['title', 'slug', 'parent', 'page', 'order', 'is_active']


class HomePageForm(StyledModelForm):
    class Meta:
        model = HomePage
        fields = [
            'site_name', 'site_tagline', 'site_phone', 'site_email', 'site_vk', 'site_telegram',
            'slider_title', 'slider_text', 'slider_image',
            'welcome_title', 'welcome_text',
            'director_name', 'director_position', 'director_image', 'director_message',
            'bento_title',
            'specialties_label', 'specialties_title', 'specialties_text',
            'specialties_image', 'specialties_count', 'specialties_list',
            'hotline_text', 'vov_text', 'vov_image',
            'contacts_title', 'contacts_address', 'contacts_phone', 'contacts_phone2',
            'contacts_email', 'contacts_hours', 'contacts_map_url',
        ]
        widgets = {
            'welcome_text': forms.Textarea(attrs={'rows': 4}),
            'director_message': forms.Textarea(attrs={'rows': 5}),
            'slider_text': forms.Textarea(attrs={'rows': 2}),
            'specialties_text': forms.Textarea(attrs={'rows': 3}),
            'specialties_list': forms.Textarea(attrs={'rows': 8}),
            'hotline_text': forms.Textarea(attrs={'rows': 5}),
            'contacts_map_url': forms.Textarea(attrs={'rows': 2}),
        }


class HomeQuickLinkForm(StyledModelForm):
    class Meta:
        model = HomeQuickLink
        fields = [
            'label', 'title', 'description', 'url', 'icon', 'style',
            'is_large', 'is_contacts', 'contacts_list',
            'stat_num', 'stat_label', 'order', 'is_active', 'open_in_new_tab',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
            'contacts_list': forms.Textarea(attrs={'rows': 4}),
            'style': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['style'].required = False
        self.fields['order'].required = False

    def save(self, commit=True):
        from .panel_utils import free_quicklink_style, next_quicklink_order
        obj = super().save(commit=False)
        if not obj.style:
            obj.style = free_quicklink_style()
        if obj.order is None:
            obj.order = next_quicklink_order()
        if commit:
            obj.save()
        return obj


class HomeBlockForm(StyledModelForm):
    class Meta:
        model = HomeBlock
        fields = ['block_type', 'title', 'content', 'order', 'is_active']
        widgets = {'content': CKEditorUploadingWidget()}

    def clean_content(self):
        return _clean_rich_html(self.cleaned_data.get('content', ''))


class BannerForm(StyledModelForm):
    class Meta:
        model = Banner
        fields = ['title', 'image', 'url', 'order', 'is_active']


class GalleryForm(StyledModelForm):
    class Meta:
        model = Gallery
        fields = ['page', 'title', 'description', 'is_active']
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}


class GalleryImageForm(StyledModelForm):
    class Meta:
        model = GalleryImage
        fields = ['image', 'title', 'description', 'order']
        widgets = {'description': forms.Textarea(attrs={'rows': 2})}


class ContentBlockForm(StyledModelForm):
    class Meta:
        model = ContentBlock
        fields = ['page', 'block_type', 'title', 'content', 'order', 'is_active']
        widgets = {'content': CKEditorUploadingWidget()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order'].required = False
        if not self.instance.pk:
            self.fields['order'].initial = 0
        if self.instance.pk and self.instance.content:
            self.initial.setdefault('content', content_for_editor(self.instance.content))

    def clean_content(self):
        return _clean_rich_html(self.cleaned_data.get('content', ''))


class ContentBlockInlineForm(StyledModelForm):
    """Форма блока внутри страницы — без поля page (FK задаёт formset)."""

    class Meta:
        model = ContentBlock
        fields = ['block_type', 'title', 'content', 'order', 'is_active']
        widgets = {'content': CKEditorUploadingWidget()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order'].required = False
        self.fields['title'].required = False
        self.fields['content'].required = False
        if not self.instance.pk:
            self.fields['order'].initial = 0

    def clean_content(self):
        return _clean_rich_html(self.cleaned_data.get('content', ''))


class EducationalProgramForm(StyledModelForm):
    class Meta:
        model = EducationalProgram
        fields = [
            'page', 'code', 'title', 'qualification', 'duration', 'form',
            'icon', 'description', 'image', 'show_on_homepage',
            'order', 'is_active',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['page'].required = False
        self.fields['order'].required = False
        if not self.instance.pk:
            self.fields['order'].initial = 0


class AdmissionYearForm(StyledModelForm):
    class Meta:
        model = AdmissionYear
        fields = ['program', 'year', 'order', 'is_active']


class ProgramDocumentForm(StyledModelForm):
    class Meta:
        model = ProgramDocument
        fields = ['year', 'doc_type', 'title', 'file', 'order', 'is_active']


ContentBlockFormSet = inlineformset_factory(
    Page, ContentBlock, form=ContentBlockInlineForm,
    extra=0, can_delete=True,
)

GalleryImageFormSet = inlineformset_factory(
    Gallery, GalleryImage, form=GalleryImageForm,
    extra=2, can_delete=True,
)

AdmissionYearFormSet = inlineformset_factory(
    EducationalProgram, AdmissionYear, form=AdmissionYearForm,
    extra=1, can_delete=True,
)

ProgramDocumentFormSet = inlineformset_factory(
    AdmissionYear, ProgramDocument, form=ProgramDocumentForm,
    extra=1, can_delete=True,
)


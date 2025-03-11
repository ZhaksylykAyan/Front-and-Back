from django.contrib import admin
from django import forms
from .models import StudentProfile, SupervisorProfile, Skill, DeanOfficeProfile
from django.core.exceptions import ValidationError
from users.models import CustomUser

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

class StudentProfileAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = CustomUser.objects.filter(role__iexact='Student').filter(student_profile__isnull=True)

    skills = forms.ModelMultipleChoiceField(queryset=Skill.objects.all(), widget=forms.SelectMultiple, required=False)

    class Meta:
        model = StudentProfile
        fields = '__all__'

    def clean_skills(self):
        """ Ensure students do not select more than 5 skills """
        skills = self.cleaned_data.get('skills', [])
        if len(skills) > 5:
            raise ValidationError("Students can select a maximum of 5 skills.")
        return skills

class SupervisorProfileAdminForm(forms.ModelForm):
    """ Custom admin form to display skill choices as a MultiSelect field """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = CustomUser.objects.filter(role__iexact='Supervisor').filter(
            supervisor_profile__isnull=True)

    skills = forms.ModelMultipleChoiceField(queryset=Skill.objects.all(), widget=forms.SelectMultiple, required=False)

    class Meta:
        model = SupervisorProfile
        fields = '__all__'

    def clean_skills(self):
        """ Ensure supervisors do not select more than 10 skills """
        skills = self.cleaned_data.get('skills', [])
        if len(skills) > 10:
            raise ValidationError("Supervisors can select a maximum of 10 skills.")
        return skills

class DeanOfficeProfileAdminForm(forms.ModelForm):
    """ Custom form to filter only dean office users in the dropdown """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = CustomUser.objects.filter(role__iexact="Dean Office").filter(dean_office_profile__isnull=True)


    class Meta:
        model = DeanOfficeProfile
        fields = '__all__'

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    form = StudentProfileAdminForm
    list_display = ('user_id', 'user', 'first_name', 'last_name', 'specialization', 'gpa', 'get_skills')
    search_fields = ('user__email', 'specialization')

    def is_profile_completed(self, obj):
        return obj.user.is_profile_completed

    is_profile_completed.boolean = True
    is_profile_completed.short_description = "Profile Completed"

    def get_skills(self, obj):
        """ Show skills in Django Admin list """
        return ", ".join([skill.name for skill in obj.skills.all()])
    get_skills.short_description = "Skills"

    def save_related(self, request, form, formsets, change):
        """ Save Many-to-Many relationships before updating profile completion """
        super().save_related(request, form, formsets, change)
        form.instance.update_profile_completion()

    def save_model(self, request, obj, form, change):
        """ Save the profile first, then assign skills """
        obj.save()  # Save the profile first (assigns an ID)
        form.instance.skills.set(form.cleaned_data.get('skills', []))  # Assign Many-to-Many field


@admin.register(SupervisorProfile)
class SupervisorProfileAdmin(admin.ModelAdmin):
    form = SupervisorProfileAdminForm
    list_display = ('user_id', 'user', 'first_name', 'last_name', 'degree', 'get_skills')
    search_fields = ('user__email', 'degree')
    list_filter = ('user__is_profile_completed',)

    def is_profile_completed(self, obj):
        return obj.user.is_profile_completed

    is_profile_completed.boolean = True
    is_profile_completed.short_description = "Profile Completed"

    def get_skills(self, obj):
        """ Show skills in Django Admin list """
        return ", ".join([skill.name for skill in obj.skills.all()])
    get_skills.short_description = "Skills"

    def save_related(self, request, form, formsets, change):
        """ Save Many-to-Many relationships before updating profile completion """
        super().save_related(request, form, formsets, change)
        form.instance.update_profile_completion()

    def save_model(self, request, obj, form, change):
        """ Save the profile first, then assign skills """
        obj.save()  # Save the profile first (assigns an ID)
        form.instance.skills.set(form.cleaned_data.get('skills', []))  # Assign Many-to-Many field


@admin.register(DeanOfficeProfile)
class DeanOfficeProfileAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'user', 'first_name', 'last_name', 'job_role')
    search_fields = ('user__email', 'job_role')
    list_filter = ('user__is_profile_completed',)

    def is_profile_completed(self, obj):
        return obj.user.is_profile_completed

    is_profile_completed.boolean = True
    is_profile_completed.short_description = "Profile Completed"

    def save_model(self, request, obj, form, change):
        """ Ensure profile completion updates when saving Dean Office profile """
        obj.save()
        obj.update_profile_completion()
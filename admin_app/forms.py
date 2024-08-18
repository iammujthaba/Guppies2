from django import forms
from store.models import Category, Product

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

class ProductForm(forms.ModelForm):
    active = forms.ChoiceField(choices=[
        (True, 'Enabled'),
        (False, 'Disabled')
    ], widget=forms.Select)

    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['active'].initial = 'Enabled' if self.instance.active else 'Disabled'

    def clean_active(self):
        return self.cleaned_data['active'] == 'True'

    def clean(self):
        cleaned_data = super().clean()
        stock = cleaned_data.get('stock')
        status = cleaned_data.get('status')

        if stock == 0 and status == 'in_stock':
            raise forms.ValidationError("Cannot set status to 'In Stock' when stock is 0.")
        elif stock > 0 and status == 'out_of_stock':
            cleaned_data['status'] = 'in_stock'

        return cleaned_data
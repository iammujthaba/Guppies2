from django import forms
from store.models import Category, Product, ShippingRate

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'image']

class ProductForm(forms.ModelForm):
    active = forms.ChoiceField(choices=[
        (True, 'Enabled'),
        (False, 'Disabled')
    ], widget=forms.Select)

    class Meta:
        model = Product
        fields = '__all__'
        exclude = ['slug', 'priority']  # Exclude slug field from the form

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

class ShippingRateForm(forms.ModelForm):
    # Define the list of states
    STATES_CHOICES = [
        ("Kerala", "Kerala"), 
        ("Karnataka", "Karnataka"),
        ("Tamil Nadu", "Tamil Nadu"),
        ("Andhra Pradesh", "Andhra Pradesh"),
        ("Arunachal Pradesh", "Arunachal Pradesh"),
        ("Assam", "Assam"),
        ("Bihar", "Bihar"),
        ("Chhattisgarh", "Chhattisgarh"),
        ("Goa", "Goa"),
        ("Gujarat", "Gujarat"),
        ("Haryana", "Haryana"),
        ("Himachal Pradesh", "Himachal Pradesh"),
        ("Jharkhand", "Jharkhand"),
        ("Madhya Pradesh", "Madhya Pradesh"),
        ("Maharashtra", "Maharashtra"),
        ("Manipur", "Manipur"),
        ("Meghalaya", "Meghalaya"),
        ("Mizoram", "Mizoram"),
        ("Nagaland", "Nagaland"),
        ("Odisha", "Odisha"),
        ("Punjab", "Punjab"),
        ("Rajasthan", "Rajasthan"),
        ("Sikkim", "Sikkim"),
        ("Telangana", "Telangana"),
        ("Tripura", "Tripura"),
        ("Uttar Pradesh", "Uttar Pradesh"),
        ("Uttarakhand", "Uttarakhand"),
        ("West Bengal", "West Bengal")
    ]
    
    state = forms.ChoiceField(choices=STATES_CHOICES, required=True)

    class Meta:
        model = ShippingRate
        fields = ['state', 'base_rate', 'additional_item_rate']
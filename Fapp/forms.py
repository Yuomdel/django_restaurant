from django.contrib.auth.forms import UserCreationForm, User
from django.contrib.auth.models import User
from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
	class Meta:
		model = Contact
		fields = ('name','email','message')

class SignUpForm(UserCreationForm):
	email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Email Address'}))
	first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'First Name'}))
	last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Last Name'}))

	class Meta:
		model = User
		fields = ('username','first_name','last_name','email','password1','password2')


	def __init__(self, *args, **kwargs):
		super(SignUpForm, self).__init__(*args, **kwargs)

		self.fields['username'].widget.attrs['class'] = 'form-control'
		self.fields['username'].widget.attrs['placeholder'] = 'User Name'
		self.fields['username'].label = ''
		self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

		self.fields['password1'].widget.attrs['class'] = 'form-control'
		self.fields['password1'].widget.attrs['placeholder'] = 'Password'
		self.fields['password1'].label = ''
		self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

		self.fields['password2'].widget.attrs['class'] = 'form-control'
		self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
		self.fields['password2'].label = ''
		self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'
  
#CART
class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Enter your full shipping address'
        }),
        required=True,
        label="Shipping Address"
    )
    
    billing_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Enter your full billing address'
        }),
        required=True,
        label="Billing Address"
    )
    
    payment_method = forms.ChoiceField(
        choices=[
            ('credit_card', 'Credit Card'),
            ('paypal', 'PayPal'),
            ('bank_transfer', 'Bank Transfer'),
            ('cash_on_delivery', 'Cash on Delivery'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='credit_card',
        label="Payment Method"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        # Add any additional validation here
        return cleaned_data

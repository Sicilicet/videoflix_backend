from rest_framework import serializers
from authentication_app.models import CustomUser
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.contrib.auth import get_user_model

signer = TimestampSigner()
User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["email", "password"]

    def create(self):
        """
        This function creates a new account as a custom user and returns it.
        """
        username = self.validated_data["email"]
        email = self.validated_data["email"]
        password = self.validated_data["password"]
        account = CustomUser(
            username=username, password=password, email=email, is_active=False
        )
        account.set_password(password)
        account.save()
        return account

    def validate_email(self, username):
        """
        This function checks if an email address already exists in the database. The username is needed because the username is equal the email address and django checks the username in the login process.
        """
        if CustomUser.objects.filter(username=username).exists():
            raise serializers.ValidationError("error")
        return username


class UserVerificationSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, token):
        """
        This function validates the token for the user verification. If it is older than 1 hour the token has expired.
        """
        try:
            email = signer.unsign(token, max_age=3600)
            user = User.objects.get(email=email)
            self.context["user"] = user
            return token
        except (SignatureExpired, BadSignature, User.DoesNotExist) as e:
            print(f"Validation failed: {e}")
            raise serializers.ValidationError("Invalid or expired token.")

    def save(self):
        """
        This function sets the is_active variable on the user to true. It is needed to verify the email address.
        """
        user = self.context.get("user")
        if user:
            user.is_active = True
            user.save()
        return user


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, token):
        """
        This function validates the token for the password reset. If it is older than 24 hours the token has expired.
        """
        try:
            email = signer.unsign(token, max_age=3600 * 24)
            user = User.objects.get(email=email)
            self.context["user"] = user
            return token
        except (SignatureExpired, BadSignature, User.DoesNotExist):
            raise serializers.ValidationError("Invalid or expired token.")

    def save(self, **kwargs):
        """
        This function saves the newly set password.
        """
        user = self.context.get("user")
        password = kwargs.get("password")
        if user and password:
            user.set_password(password)
            user.save()

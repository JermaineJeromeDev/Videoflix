from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for validating and creating a new user registration."""

    confirmed_password = serializers.CharField(write_only=True)

    email = serializers.EmailField()

    class Meta:
        """Meta options for RegisterSerializer."""

        model = User
        fields = ["id", "email", "password", "confirmed_password"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        """Verify that passwords match and the email is not already taken."""
        if data["password"] != data["confirmed_password"]:
            raise serializers.ValidationError(
                "Bitte überprüfe deine Eingaben und versuche es erneut."
            )
        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError(
                "Bitte überprüfe deine Eingaben und versuche es erneut."
            )
        return data

    def create(self, validated_data):
        """Create an inactive user instance after validation passes."""
        validated_data.pop("confirmed_password")
        return User.objects.create_user(**validated_data)

from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSignUPSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("nickname","password","email")
    def create(self,validated_data):
        password = validated_data.pop("password",None)
        if password is None:
            raise ValueError("password is required")
        return User.objects.create_user(
            password = password,
            **validated_data
        )

class UserProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ("nickname","email","password")
        read_only_fields  =("email",)

    def update(self, instance, validated_data):
        instance.nickname = validated_data.get("nickname",instance.nickname)
        password = validated_data.get("password",None)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    def validate(self,data):
        email = data.get("email")
        password = data.get("password")
        if email and password:
            user = authenticate(
                request=self.context.get("request"),
                email = email,
                password = password
            )
            if not user:
                raise serializers.ValidationError(
                    detail="유저 정보가 맞지 않습니다.", code="authenticate"
                )
        else:
            raise serializers.ValidationError(
                detail="이메일과 비밀번호는 필수입니다.",
                code = "authenticate",
            )
        data["user"] = user
        return data



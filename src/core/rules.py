from django.core.validators import DecimalValidator, EmailValidator


def get_rules(serializer_field, field_type):
    """
    필드에 대한 validation 체크를 Front단에서도 처리할 수 있도록하기 위해 메타정보로 rules를 생성해줍니다.
    """
    rules = []

    if serializer_field.required:
        rules.append(
            {"required": True, "message": serializer_field.error_message["required"]}
        )

    if field_type:
        rules.append({"type": field_type, "message": f"Invalid {field_type}"})

    for validator in serializer_field.validators:
        if validator.code == "max_length":
            rules.append(
                {
                    "max_length": validator.limit_value,
                    "message": validator.message or "Empty Message",
                }
            )
        elif validator.code == "min_length":
            rules.append(
                {
                    "min_length": validator.limit_value,
                    "message": (str(validator.message) or "Empty Message"),
                }
            )
        if validator.code == "max_value":
            rules.append(
                {
                    "max_value": validator.limit_value,
                    "message": (str(validator.message) or "Empty Message"),
                }
            )
        elif validator.code == "min_value":
            rules.append(
                {
                    "min_value": validator.limit_value,
                    "message": (str(validator.message) or "Empty Message"),
                }
            )
        elif isinstance(validator, DecimalValidator):
            rules.append(
                {"type": "decimal", "message": validator.message or "Empty Message"}
            )
        elif isinstance(validator, EmailValidator):
            rules.append(
                {"type": "email", "message": validator.message or "Empty Message"}
            )
        elif validator.code == "invalid":
            re_pattern = validator.regex
            rules.append(
                {
                    "regexp": re_pattern.pattern.replace(r"\Z", ""),
                    "message": validator.message or "Empty Message",
                }
            )

        # TODO: 변경 또는 추가되는 타입에 대한 rules 추가

    return rules

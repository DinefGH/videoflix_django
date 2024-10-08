from django.contrib.auth.tokens import PasswordResetTokenGenerator

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    Generates a token for user account activation.

    This class extends the `PasswordResetTokenGenerator` to create tokens for
    account activation based on user ID, timestamp, and the user's activation status.
    """
    def _make_hash_value(self, user, timestamp):
        """
        Generates a hash value for the token.

        Args:
            user: The user object for which the token is being generated.
            timestamp: The timestamp when the token is created.

        Returns:
            str: A hashed value combining the user ID, timestamp, and the user's activation status.
        """
        return (
            str(user.pk) + str(timestamp) + str(user.is_active)
        )

account_activation_token = AccountActivationTokenGenerator()
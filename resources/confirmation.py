from time import time
import traceback

from flask import request, render_template, make_response
from flask_restful import Resource

from models.confirmation import ConfirmationModel
from models.user import UserModel
from schemas.confirmation import ConfirmationSchema
from libs.mailgun import MailGunException

NOT_FOUND = "Confirmation reference not found."
EXPIRED = "The link has expired"
ALREADY_CONFIRMED = "Registration has already been cofirmed."
USER_NOT_FOUND = "User not found."
RESEND_FAIL = "Internal server error. Failed to resend confirmation email."
RESEND_SUCCESSFUL = "E-mail confirmation successfully re-sent."

confirmation_schema = ConfirmationSchema()


class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        """Returns confirmation HTML page"""
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            return {"message": NOT_FOUND}, 404

        if confirmation.expired:
            return {"message": EXPIRED}, 400

        if confirmation.confirmed:
            return {"message": ALREADY_CONFIRMED}, 400

        confirmation.confirmed = True
        confirmation.save_to_db()

        headers = {"Content-Type": "text/html"}
        return make_response(
            render_template("confirmation_page.html", email=confirmation.user.email),
            200,
            headers
        )

class ConfirmationByUser(Resource):
    @classmethod
    def get(self, user_id: int):
        """Returns confirmations for a given user. Use for testing."""
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        
        return (
            {
                "current_time": int(time()),
                "confirmation": [
                    confirmation_schema.dump(each) for each in user.confirmation.order_by(ConfirmationModel.expire_at)
                ],
            },
            200,
        )

    def post(self, user_id):
        """
        This endpoint resend the confirmation email with a new confirmation model. It will force the current
        confirmation model to expire so that there is only one valid link at once.
        """
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404

        try:
            # find the most current confirmation for the user
            confirmation = user.most_recent_confirmation  # using property decorator
            if confirmation:
                if confirmation.confirmed:
                    return {"message": ALREADY_CONFIRMED}, 400
                confirmation.force_to_expire()

            new_confirmation = ConfirmationModel(user_id)  # create a new confirmation
            new_confirmation.save_to_db()
            # Does `user` object know the new confirmation by now? Yes.
            # An excellent example where lazy='dynamic' comes into use.
            user.send_confirmation_email()  # re-send the confirmation email
            return {"message": RESEND_SUCCESSFUL}, 201
        except MailGunException as e:
            return {"message": str(e)}, 500
        except:
            traceback.print_exc()
            return {"message": RESEND_FAIL}, 500

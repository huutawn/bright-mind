from .models import Donation, Withdrawal, Proof, ProofImage
from .schemas import DonationResponse, WithdrawalResponse, ProofResponse, ProofImageResponse


class TransactionMapper:
    @staticmethod
    def to_donation_response(donation: Donation):
        return DonationResponse.model_validate(donation)

    @staticmethod
    def to_withdrawal_response(withdrawal: Withdrawal):
        return WithdrawalResponse.model_validate(withdrawal)

    @staticmethod
    def to_proof_response(proof: Proof):
        return ProofResponse.model_validate(proof)

    @staticmethod
    def to_proof_image_response(proof_image: ProofImage):
        return ProofImageResponse.model_validate(proof_image)

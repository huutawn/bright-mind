from .models import Withdrawal, Proof, ProofImage
from .schemas import WithdrawalResponse, ProofResponse, ProofImageResponse

class WithdrawalMapper:
    @staticmethod
    def to_withdrawal_response(withdrawal: Withdrawal):
        return WithdrawalResponse.model_validate(withdrawal)

    @staticmethod
    def to_proof_response(proof: Proof):
        return ProofResponse.model_validate(proof)

    @staticmethod
    def to_proof_image_response(proof_image: ProofImage):
        return ProofImageResponse.model_validate(proof_image)
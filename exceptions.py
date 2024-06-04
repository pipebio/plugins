
class UserFacingException(Exception):
    """
    Specific exception, which will display a message to the user. To be used when the problem is not due to a bug, AND
    at least one of the following applies:

    - The user can fix the problem in some way. E.g. malformed file for import, too strict filter, a parameter
      selection (done by the users) is inconsistent, user is trying to run the tool with the wrong number or wrong
      type of documents etc. OR
    - The problem is not fixable, but due to something wrong with the data that the user can understand. This
      can happen if the data is too poor quality for the algorithm to work correctly. E.g. user is
      trying to assemble  reads to a reference, but none of the reads match the reference.
      Or user is trying to quality-trim reads, and all reads are filtered away due to poor sequencing quality.

    If the error doesn't fit the above situations, then please use the parent class PipeBioException.
    """
    user_message: str
    pass

    def __init__(self, user_message: str):
        """
        :param user_message: shown to users.

        Do not include sensitive data!

        Include a short, concise message about what went wrong and/or how it can be fixed.

        Aim to empower the user for success the next time. Try to describe what it takes to get success, instead of
        just describing what they did "wrong". Examples:

        - "Only nucleotide databases are supported" instead of "Amino acid databases are not supported".
        - "Only the characters A, C, G, T are supported. Seq10 contained 'X'" instead of "Unsupported character: X."
        """
        self.user_message = user_message
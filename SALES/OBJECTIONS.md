# Sales Objections

## "We already have IAM."

Response: IAM answers who may access a resource. Action Gate addresses whether this specific agent action was authorized under the relevant policy and execution context, and places enforcement at the protected-tool boundary. It complements IAM rather than replacing it.

## "We already log agent activity."

Response: logging after execution is not the same control as preventing an unauthorized tool call. The pilot tests the enforcement boundary directly.

## "Our agent framework already has permissions."

Response: keep it. Action Gate can sit downstream as an independent execution check. The question is whether the final protected tool will independently reject an unapproved or replayed action.

## "We need compliance."

Response: the product can provide evidence for defined controls, but it does not automatically confer a regulatory certification. Compliance scope must be mapped to the customer's requirements.

## "Can you guarantee the agent will never do something unsafe?"

Response: no. The product makes a narrower, testable claim: specified protected execution paths can be governed and tested at the authorization boundary.

## "Why not build this ourselves?"

Response: a customer can. The commercial value is the deployable boundary, integration contract, acceptance suite, evidence model, release discipline and support around it.

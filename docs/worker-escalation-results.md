# Worker escalation candidate qualification

Local implementation in progress, 2026-11-02. This is a source candidate, not a
published release or installed policy. Preview.14 remains the released selection.

The [selected design](worker-routing-design.md#selected-design-primary-luna-and-one-escalation-target)
and [implementation plan](codex-plus-plan.md#selected-plan-primary-luna-and-optional-escalation)
keep the native primary, useful Luna assignments and one opt-in escalation
route. The two adaptive skills use request/applicable user guidance with no new
configuration file. Terra can select Sol or Astra; Sol can select Astra. The
existing explicit Luna workflows stay Luna-only. Children return gaps to their
initiating primary without recursively applying a new escalation policy.

Source, package, model execution, behavior and deployment evidence will be
recorded separately after qualification. Private native captures remain outside
committed source. Local Terra-primary inference remains unavailable from the
previous spike and is not retried in this pass.

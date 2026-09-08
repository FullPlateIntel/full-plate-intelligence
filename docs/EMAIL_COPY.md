# EMAIL_COPY.md — confirmation and welcome e-mail drafts (prelaunch)

These are drafts for the Kit form "incentive/confirmation" e-mail and the first welcome e-mail.
They are written for the prelaunch state (Full Plate Weekly has not started sending). Placeholders in
`[BRACKETS]` must be filled with confirmed facts; never invent an address or sender.

## Confirmation e-mail (Kit form: "Send confirmation email" ON, "Auto-confirm" OFF)

Subject: Please confirm your email for Full Plate Weekly

> Thanks for signing up. Click the button below to confirm your email address and join the Full Plate Weekly list.
>
> [Confirm my email]
>
> Full Plate Weekly is a free newsletter with practical financial insights for independent restaurant owners. It starts sending when the first issue is ready; you'll also hear when The Full Plate Show, the Restaurant Intelligence Index, and Full Plate Benchmark launch.
>
> If you didn't sign up, ignore this email and nothing will be sent.
>
> Steve Dillberg, Full Plate Intelligence

## Welcome e-mail (sent once after confirmation)

Subject: You're on the list

> Welcome, and thank you for confirming.
>
> Here's what to expect: one short email a week once Full Plate Weekly launches, written by me, covering the numbers that decide whether a restaurant grows, struggles, or thrives: food cost, labor, occupancy, cash flow, and profit. No fluff.
>
> Until the first issue, you'll only hear from me about launch news. You can reply to this email with a question anytime; I read every one.
>
> Steve Dillberg
> Founder, Full Plate Intelligence

Footer (required on every send; Kit inserts the address and unsubscribe link from the account profile):

> Full Plate Intelligence [OPERATING ENTITY, CONFIRM] · [POSTAL ADDRESS, CONFIRM — not a personal home address]
> You're receiving this because you confirmed your email at fullplateintel.com. Unsubscribe | Update preferences

## Checks before the launch label

- Sender identity: `From` name and address confirmed (e.g. Steve Dillberg <steve@fullplateintel.com>); the mailbox must accept replies.
- SPF, DKIM (Kit's CNAME records) and DMARC alignment verified from a delivered message's headers, not from the DNS panel alone.
- One-click unsubscribe (`List-Unsubscribe` / `List-Unsubscribe-Post`) present in delivered headers; unsubscribe link works and suppresses the address.
- Confirmation e-mail arrives for a new test address; re-submitting the same unconfirmed address does not flood the inbox (see runbook step 6).
- No promise that an issue or report is "on its way".

# Integrated anonymous reading — V5

Source owner: Fountain-Coach/fountain.coach
Reusable renderer: Fountain-Coach/fountain-press (unchanged)
Status: disposable WLAN fixture, no public deployment

## What is being proved

The source-neutral publication ontology survives opening a book:

1. containing space is perceptible as an inherited colored physical rail;
2. the selected anonymous book is uniquely identified amongst its siblings;
3. the unmarked circle returns to the correct containing space;
4. adjacent books are reachable without returning to an unrelated catalogue;
5. turning pages operates on stable page addresses, and a tentative
   under-threshold swipe settles back without changing the address;
6. page geometry stays consistent across iPad portrait, landscape and phone;
7. the same anonymous book keeps its token across differently colored spaces.

No source artwork, Scores, editorial titles or manufactured paragraphs were
introduced. Three blank fixture leaves are *not* a demonstration of typography
quality. An actual reading-content experience remains a separate proof.

## Verification

- Generated fixture passes source-independent structural verification.
- Browser tests assert paper ratio around 0.707, no horizontal overflow,
  current sibling identity, circle parent return, sibling links, gesture
  cancellation and accepted swipe, keyboard/page buttons, history and
  invalid-address refusal in three device sizes.
- Original V38 source/reader regressions must pass separately.
- No cross-document morph animation accepted; its experimental attempt
  was excluded after a navigation reliability failure.

See the adjacent screenshots and release receipt for the staged result.

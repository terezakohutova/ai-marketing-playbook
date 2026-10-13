# Sample inventory exports: one storefront, two marketplaces

Three files, one per sales channel, in the shape a seller dashboard exports:

- `storefront.csv`: the source of truth for what is actually in stock (the files don't say so; the agent has to work it out).
- `marketplace-a.csv`, `marketplace-b.csv`: the same items listed on two marketplaces.

Every item is invented. The data contains planted cases of the kinds the pattern is about, including ones where trusting the "sold" signal would be wrong; they are not listed in this folder, so a run against it is a blind test. [`proposal-queue-output.md`](proposal-queue-output.md) is the unedited output of a fresh agent run, and `python tools/reference_check.py inventory examples/sample-run` prints what the written rules alone produce.

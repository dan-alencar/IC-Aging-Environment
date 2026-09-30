# References

`fixed_pnr.dcp` is preserved here only as a historical reference checkpoint.
It is not added to the Vivado project and is not required for normal project
creation, synthesis, implementation, or bitstream generation.

The active portable replacement is:

```text
src/constraints/fixed_pnr_constraints.xdc
```

That XDC captures the fixed placement and `FIXED_ROUTE` constraint used by the
aging study. If the checkpoint must be audited or regenerated, use:

```bash
scripts/extract_fixed_pnr_constraints.sh
```

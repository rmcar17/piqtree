
<a id='changelog-0.6.1'></a>
# Changes in release "0.6.1"

## Contributors

- @GavinHuttley docs
- @rmcar17 dependencies

## BUG

- Pin build dependencies for reproducible builds and use new delvewheel `get_all_needed` API.

## DOC

- Update examples to the latest Cogent3 API.

<a id='changelog-0.6.0'></a>
# Changes in release "0.6.0"

## Contributors

- @rmcar17 and @thomaskf enabled windows support for piqtree!

- @rmcar17 ensured `nj_tree` raises an appropriate error on NaN input.

- @rmcar17 reworked `random_trees` and the related app to become `random_tree`, returning a single tree.

- @rmcar17 and @thomaskf integrated IQ-TREE 3 into piqtree.

- @rmcar17 added support for Lie Markov Model prefixes.

- @rmcar17 added the STRSYM and UNREST models.

- @rmcar17 added source tracking for the inputs of apps.

- @rmcar17 and @thomaskf integrated consensus tree contruction into `piqtree`.

- @rmcar17 added support for the parameterisation of currently supported models, base frequencies, and rate heterogeneity.

## ENH

- Added windows support!

- Add `random_tree` and `piqtree_random_tree`. The function and app have the same parameters as the `random_trees` and `piqtree_random_trees` versions, except the `num_trees` argument has been removed.

- `piqtree` now uses IQ-TREE 3 for its internal library.

- Add support for Lie Markov Model prefixes.

- Add the STRSYM and UNREST models.

- `piqtree` apps now track the sources of their inputs.

- Add a method for building consensus trees with specifiable support parameters.

- Add a consensus tree app.

- Substitution models, base frequencies, and models for rateheterogeneity can now be parameterised.

## BUG

- An error is now raised when calling `nj_tree` with NaN distances instead of failing silently.

## API

- Split Lie Markov Models out of the standard dna enum.

- Remove unused `rand_seed` from `fit_tree`.

- All apps have been renamed to take the form `piq_<func_name>`.

- `random_trees` and `piqtree_random_trees` have been removed in favour of `random_tree` and `piq_random_tree`. Looping can be used if multiple trees are needed.

<a id='changelog-0.5.0'></a>
# Changes in release "0.5.0"

## Contributors

- @GavinHuttley added `nj_tree` as a hook for `cogent3.Alignment.quick_tree`.
- @YapengLang handled negative branch lengths from the rapidNJ tree.
- @rmcar17, @thomaskf general maintanence on the piqtree/IQ-TREE sides including work on windows behind the scenes.

## ENH

- Add support for Python 3.13, remove support for 3.10
- IQ-TREE's rapidNJ implementation can be used as a hook for `quick_tree` on `cogent3` alignment objects. Try `Alignment.quick_tree(use_hook="piqtree")`.
- `nj_tree` now by default does not allow negative branch lengths. Set `allow_negative=True` if this behaviour is desired.
- Allow `str` to be used for `model` in `build_tree` and `fit_tree`. The value is automatically coerced into the `Model` class.

## API

- Simplify API for `piqtree_phylo` and `piqtree_fit` apps. Both now take a single parameter for the model, matching the parameter for `model` in `build_tree` and `fit_tree`.

<a id='changelog-0.4.0'></a>
# Changes in release "0.4.0"

## Contributors

- @rmcar17 integrated new functions from IQ-TREE in Python, added multithreading support, and wrote the API refererence and quickstart.
- @thomaskf exposed all new functions from IQ-TREE to be available from Python, and worked on multithreading support.
- @GavinHuttley worked on setting up and writing the documentation and associated devtools, ModelFinder, and integration with `cogent3` apps.
- @YapengLang worked on bootstrapping support and extracting model parameters
- @KatherineCaley worked on processing the ModelFinder results.

## ENH

- piqtree2 renamed piqtree to support future major releases of IQ-TREE.
- piqtree now supports multithreading!
- New function `nj_tree` constructs a rapid neighbour-joining tree from a pairwise distance matrix.
- New function `model_finder` finds the best model for a given alignment.
- New function `jc_distances` constructs a pairwise JC distance matrix from an alignment.
- New function `make_model` allows converting an IQ-TREE string representation of a model to a `Model` class.
- API for `random_trees` has changed - new order (`num_trees`, `num_taxa`, `tree_mode`, then `rand_seed`).
- API for `robinson_foulds` has changed - now accepts a Sequence of trees.
- Model parameters are now extracted from IQ-TREE where for now possible.
- `build_tree` now supports ultrafast bootstrapping.
- `Model` creation is now more robust.
- Use `piqtree.__iqtree_version__` to see what version of piqtree is being used.
- See what can now be done in our [new documentation](https://piqtree.readthedocs.io)!

## DOC

- [Documentation](https://piqtree.readthedocs.io) is now on readthedocs!

<a id='changelog-0.3.1'></a>
# Changes in release "0.3.1"

## ENH

- Add support for Lie Markov Models.
- Base frequencies default to None (specified by model).

## BUG

- `piqtree2` apps are now pickleable (they can now be run with `parallel=True` in the cogent3 app infrastructure)

<a id='changelog-0.3.0'></a>
# Changes in release "0.3.0"

## Contributors

- @rmcar17 Added new classes to enhance model specification when calling `build_tree` and `fit_tree`.
- @thomaskf fixed a bug in IQ-TREE resulting in segmentation faults on some invalid arguments.

## ENH

- `build_tree` and `fit_tree` now allow specifying base frequencies, invariable sites and rate heterogeneity options.

## BUG

- Fixed a segmentation fault on repetitive calls to IQ-TREE with particular arguments.

<a id='changelog-0.2.0'></a>
# Changes in release "0.2.0"

## Contributors

- Richard Morris
- Robert McArthur

## ENH

- `build_tree` and `fit_tree` now use enums for the substitution model.

## BUG

- Fixed an issue where calling `build_tree` or `fit_tree` twice, then another function with invalid input resulted in a segmentation fault.

## DOC

- Implement scriv as a tool to manage collection of changes, and automated collation into the changelog

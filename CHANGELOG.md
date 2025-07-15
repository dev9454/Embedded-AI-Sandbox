## [0.3.0-beta.3](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/compare/v0.3.0-beta.2...v0.3.0-beta.3) (2025-07-14)

### Features

* [HOL-156] Added histogram plotting for analysis ([70bd0f0](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/70bd0f0a3e2a772bb094b15b45d495271bdddfac))
* [HOL-156] Generate trace file for onnx ([b2ee162](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/b2ee1625d05e0cd7c7f0bb4aca255a2a3224d90c))
* [HOL-156] Plotting trace files too ([6f58c3d](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/6f58c3de5b47f5dbc21c3a3f86618d2bb6c4c895))
* **ui:** add comparison with reference onnx by default ([3d1dbf9](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/3d1dbf92cfa007b9690333257fd5be4393737563))
* Ambarella backend takes in bitwidth ([7031259](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/7031259a5b45f0568d1a96619330bc775a663a5e))
* Enable onnx simplifier ([094a472](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/094a4725a4b9f35b215ce5a3f2a69b4cda857d07))
* Expose quantization styles DRAV2 and DRAV3 for Ambarella ([cbdcf72](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/cbdcf72a35d6db43d9aa696ee837bd6bc7f2ecd9))
* run_inference call also returns execution time ([62ddd77](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/62ddd77d0c64d119ba33d8f34fd001b086b36539))
* Set Quantization style ([2017e6d](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/2017e6d1b30f3808f79e93aa8b8bfebffa17f7c9))
* Simplified information shown after inference ([4cd434f](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/4cd434f7d9d3ef1369c20b7364e4aa7965d9e883))
* TI quantization styles exposed ([914c027](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/914c0273a2286d12d38d34422ecf69e966c37a66))
* Validation checks for quantization types ([ae512e5](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/ae512e5e089748298cc3c22b30002e378ffe0208))

### Bug Fixes

* [HOL-156] Account for dtype while inserting onnx trace outputs ([78f1f2e](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/78f1f2e6c664cb08621262258ca428ce531ab905))
* [HOL-156] fix issue where TIDL backend does not generated traces ([3633dff](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/3633dff66e824adeb52796640d1fcdbdad88e050))
* [HOL-156] Make histogram y axis log scale ([760b965](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/760b96548b37dd59673b4b589dd1e48050c99e99))
* [HOL-156] Redundant import ([6a4a8ad](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/6a4a8adf263549a2d5d945a07d841717695d6d2c))
* [HOL-171] Ambarella backend no jump host issue ([0fabbd9](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/0fabbd9a7dbd9e29a4177bd09691112d3040780a))
* [HOL-171] Ambarella plots and Quantization analysis enabled ([7fef7ab](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/7fef7ab188d8ce451ac59ed0122b3000d1a57f11))
* [HOL-177] TI import failure feedback ([a742b05](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/a742b05331c23eae7ecf6319797e26cc01931d60))
* [HOL-182] Bugfix in the unsupported layer feature ([c59f34a](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/c59f34a8eeed71ed7458ff518ee4b0c94c51603b))
* Added overwrite working dir and other features ([850f0a6](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/850f0a63ca43051a1c58df33f17c09d2f72b13ec))
* Bug in onnxwrapper ([455ef29](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/455ef29c437c877d58cfc49ff2b720de2aea5b12))
* Debug tracing argument had an issue for TI on target ([7506e27](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/7506e2759679b22737bc0a2c635709a1a66564fa))
* Docker image name was incorrect ([d6340f9](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/d6340f9b673da1406f13d0351a2c93481df353e6))
* **ui:** Install streamlit in the startup script for now ([20a4be9](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/20a4be973c60760ab3970f2675d5bec587fff5e7))
* Layernames with : were not being parsed ([4b17ed9](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/4b17ed91bc1b1ed5b8ad5ebf289747c24e0590da))
* Make workingdir path absolute ([6142ad8](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/6142ad8bde005081222d16aa4683ce7eab15683c))
* Moved logging to a separate source file ([afe3b96](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/afe3b96769580ad9d1f37e0dc0565617d8e95532))
* onnxrt_api maintains input order ([65539ca](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/65539ca916d2bf12a74e25d635e3f15a01438090))
* UI updated to be simpler ([0ee21f5](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/0ee21f585454108fdf59c3b1df0da9263ef3f2b9))

### Code Refactoring

* Change name of a plot ([cdc00c4](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/cdc00c416e073290c4ace5c33e69fc4f9073dd25))
* Description of cmd line arguments updated ([bbc83e1](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/bbc83e1a4f5e3893c03ef0070c169eec9e52c8aa))

### Documentation

* Adding guidelines for contributing to the repo ([7c40160](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/7c401602585233f1534ff9bdfc8250b276540b90))
* Conventional commits ([bdce1b9](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/bdce1b9a3160e7c5cb9cc2791a1eec0ffb1d0b3d))
* Setting up insecure registries ([9663504](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/96635048706f1d81f6a0ee79364d14281c681edc))
* Update README.md ([a643f3a](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/a643f3a7c15b697ffc4de3f429e71ef9aa6b40cf))
* Update README.md ([38bcebd](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/38bcebde4131fd8fb37f986e81805f30766a887f))
* Updated with docker trouble shooting ([9c8b640](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/9c8b6401407ade336ea701aa0aa65048248c5b8d))

### Tests

* Add demos to pytest ([795c121](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/795c1216a493ddf4dbd79b0f7f758c7c152f5dff))
* fix host emulation test for ti ([3f8376c](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/3f8376c843b04d5048219cfe5366ace592465621))
* Make pytest ignore INFO logs ([4efa64d](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/4efa64dea360772a73a9fcb0af1834c384a915e7))

## [0.3.0-beta.2](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/compare/v0.3.0-beta.1...v0.3.0-beta.2) (2025-06-10)

### Bug Fixes

* [HOL-148] typo ([e43e947](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/e43e947d45e2c014e9ebaa87fbb7b376b714f9fc))
* [HOL-87] Smaller separate docker for TI ([c944b20](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/c944b2034bd61860d6470045cf8c1ad094ee5b9f))

### Documentation

* [HOL-148] Instruction to download a single branch ([0207541](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/020754126f7a48a7343bfb1047a898a1b1fbb289))
* [HOL-148] Link to report a but / request a feature ([0b14bf4](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/0b14bf4fc00ad0ae4fecd6679ee786b803b8e8d0))

## [0.3.0-beta.1](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/compare/v0.2.0...v0.3.0-beta.1) (2025-06-05)

### Features

* **HOL-98:** Add verbosity option to the logging ([d7e04e4](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/d7e04e42451d9e8d4380950451d3854222733905))
* compile_only flag argument added ([a015810](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/a0158102161f126aec382ae17054a967fb4b23ea))
* TIDL backend writes the quant txt proto ([9d4bc88](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/9d4bc88c4f6ea6dd2b7ce54bbc48a4b2bd9c9421))

### Bug Fixes

* **HOL-80:**  Manage the working directory life cycle ([c1c711b](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/c1c711b61c890af032d3be80fe929b06f5c11790))
* [HOL-100]  firmware flashing bug ([4367ad9](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/4367ad95f32d6d01420d72ac2c6b50d25983da65))
* Edit .gitlab-ci.yml ([7102a48](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/7102a48286f0a7236a50854a43e20d5c87e69846))
* Edit .gitlab-ci.yml ([d223142](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/d223142d531b120a1a4026e3560ce6a3ba3c8ac1))
* Edit .gitlab-ci.yml ([013b25f](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/013b25fbd136d1b6a27b7587e4a2e540242949e6))
* Edit .releaserc.yml ([da457d5](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/da457d5e0d89e7ecba22921867560555d595a983))
* Enable semantic versioning ([edfff8c](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/edfff8cb4cf302c56fb2d86bf0ab25ffd825bb16))
* ti data convert numbv issue ([66d0cb1](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/66d0cb19ff63ce96d1e9f894673ed4708fc7e3b3))

### Code Refactoring

* cleanup unnecessary files ([a43d28f](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/a43d28fa5b35a59198da22e449321d4c107a27e4))
* custom formatter ([4e4914d](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/4e4914d6f5024a8db81e518168048e690bedc6e0))
* deplomentInfo class ([0d5be23](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/0d5be23dff8aba38583ba843c328288f0c8c9a7d))
* deploymentInfo class somemore ([cf37a60](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/cf37a608a70da3c6e1e981b6cb9188937dbf7fe5))
* parse_commandline_args ([0a682f5](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/0a682f5ff5a56da327e24637000ef227b172d644))
* remove private vscode files ([fbc120c](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/fbc120c2f1652768b29cc758f8477037f6595af4))

### Continuous Integration

* add linting ([0892712](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/0892712ffe4beae0c4ee3e72be0eda7287a3fa12))

### Tests

* Compilation test for Ambarella and TDA4VH added ([60c7b60](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/60c7b600a588b7cbacf5dcd7cca49449daad95fd))
* h5writer class unit tests ([cf2c329](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/cf2c329deac3080cb3126c2fedc9a2c88e05ec8e))
* is_in_list ([d5d494b](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/d5d494b5a2e97da39869e7a8adf56be88a6ce8eb))
* More tests for the ti flow ([2c0423f](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/2c0423f055225b7260ff0246ac9686ac17561e79))
* onnx wrapper ([48d1b96](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/48d1b96d9f4fbb4ef6f65d39b22f3fd907e588ac))
* unit tests for tensor class ([bef00e6](https://gitlab.aptiv.today/embedded-ai-factory/tools/foundry/commit/bef00e611d761c7c5e1d1c72aec5a4e030e1afea))

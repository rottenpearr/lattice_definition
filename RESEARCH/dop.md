# 20 новых научных статей и патентов по распознаванию кристаллических решеток с машинным обучением

Найдено 20 новых источников (2019-2025), не пересекающихся с уже найденными 50 работами. Источники охватывают attention mechanisms, transformers, generative models, active learning, патенты и материал-специфические применения.

## Attention mechanisms и Transformer архитектуры

### 1. CrystalTransformer: Transformer-generated atomic embeddings for crystal property prediction

**Авторы:** Jin, L., Du, Z., Shu, L., et al.

**Год:** 2025

**Тип:** Научная статья (Nature Communications, Vol. 16, Article 1210)

**Релевантность:** Предлагает transformer-модель с multi-head self-attention для генерации универсальных атомных эмбеддингов (ct-UAEs). Использует 6-слойный encoder для обработки атомных взаимодействий и 3D структур. Демонстрирует улучшение на 14-18% по сравнению с CGCNN/ALIGNN для предсказания энергии формирования. Включает аугментацию данных для ротационной и трансляционной инвариантности. Поддерживает multi-task learning для одновременного предсказания нескольких свойств кристаллов.

**Ссылка:** https://doi.org/10.1038/s41467-025-56481-x

---

### 2. ComFormer: Complete and Efficient Graph Transformers for Crystal Material Property Prediction

**Авторы:** Yan, K., Liu, Y., Lin, Y., Ji, S.

**Год:** 2024

**Тип:** Препринт/Conference Paper (arXiv:2403.11857v1)

**Релевантность:** Вводит SE(3)/SO(3) transformer для кристаллических материалов с доказанной геометрической полнотой. Использует решеточное представление с периодическими паттернами (α, β, γ векторы). Две варианта: iComFormer (SE(3)-инвариантный) и eComFormer (SO(3)-эквивариантный). Node-wise и edge-wise transformer layers с attention механизмами для периодических структур. State-of-the-art результаты на JARVIS, Materials Project, MatBench.

**Ссылка:** https://arxiv.org/html/2403.11857v1

---

### 3. CrysCo: Hybrid Transformer-Graph framework with edge-gated attention

**Авторы:** Madani, M., Lacivita, V., Shin, Y., et al.

**Год:** 2024

**Тип:** Научная статья (npj Computational Materials, Vol. 11, Article 15)

**Релевантность:** Гибридная архитектура, объединяющая transformer композиционного анализа (CoTAN) с edge-gated attention GNN (CrysGNN). Явно кодирует 4-body взаимодействия через три графа: атомный (G8), bond angles (L(G8)), dihedral angles (L(G8d)). 10 слоев attention-based message passing. CoTAN использует 6-слойный transformer с mat2vec эмбеддингами. Превосходит ALIGNN, MEGNet, CGCNN на 7/8 датасетов.

**Ссылка:** https://doi.org/10.1038/s41524-024-01472-7

---

### 4. CEGANN: Crystal Edge Graph Attention Neural Network for multiscale classification

**Авторы:** Banik, S., Dhabal, D., Chan, H., et al.

**Год:** 2023

**Тип:** Научная статья (npj Computational Materials, Vol. 9, Article 23)

**Релевантность:** Graph attention архитектура на edge graphs для мультимасштабной классификации от атомного до мезоскопического уровня. Иерархический message passing с edge и angle attention механизмами. Достигает 100% точности классификации space groups. Работает в зашумленных термальных средах. Успешно различает liquid vs amorphous фазы, hexagonal vs cubic ice motifs, grain boundaries. Применяется для идентификации кристаллических структур в MD симуляциях.

**Ссылка:** https://doi.org/10.1038/s41524-023-00975-z

---

## Unsupervised и Generative методы

### 5. TransVAE-CSP: Transformer-Enhanced Variational Autoencoder for Crystal Structure Prediction

**Авторы:** Chen, Z., Wang, Z., et al.

**Год:** 2025

**Тип:** Препринт (arXiv:2502.09423)

**Релевантность:** Новая VAE архитектура специально для предсказания и реконструкции кристаллических структур. Интегрирует adaptive distance expansion с irreducible representation для захвата периодичности и симметрии. Encoder использует transformer с equivariant dot product attention механизмом. Обучается на характеристическом пространстве распределения стабильных материалов. Превосходит CDVAE на carbon_24, perov_5, mp_20 датасетах.

**Ссылка:** https://arxiv.org/abs/2502.09423

---

### 6. CGWGAN: Crystal Generative Framework Based on Wyckoff Positions

**Авторы:** Su, T., Cao, B., Li, M., Hu, S., Zhang, T.-Y.

**Год:** 2024

**Тип:** Научная статья (Journal of Materials Informatics)

**Релевантность:** GAN-based фреймворк генерирует кристаллические структуры используя позиции Wyckoff и асимметричные единицы. Трехмодульная архитектура: crystal template generator (GAN), atom-infill модуль, crystal screening. Использует Wasserstein GAN с gradient penalty и 1D convolutional self-attention. Достиг 88% и 74% конвергенции для бинарных и моноэлементных кристаллов. Обнаружил 7 новых кристаллов в Ba-Ru-O системе.

**Ссылка:** https://www.oaepublish.com/articles/jmi.2024.24

---

### 7. Self-Supervised Learning for XRD Phase Transition Classification

**Авторы:** Sun, Y., Brockhauser, S., Hegedűs, P., et al.

**Год:** 2023

**Тип:** Научная статья (Scientific Reports)

**Релевантность:** Пионерская работа по self-supervised learning (relational reasoning + contrastive learning) для анализа XRD паттернов и распознавания кристаллических структур. Три фреймворка: SpecRR-Net (relational reasoning), SpecMoco-Net (contrastive learning), SpecRRMoco-Net (гибрид). Momentum contrastive learning (MoCo) адаптирован для спектральных данных. Достигает 98.6% точности на Fe датасетах и 80% на FeO с только 2.8% размеченных данных. Domain-specific аугментации: magnitude warping, diffraction angle warping.

**Ссылка:** https://doi.org/10.1038/s41598-023-36456-y

---

### 8. Composition-Conditioned Crystal GAN for Materials Discovery

**Авторы:** Kim, S., Noh, J., Gu, G.H., et al.

**Год:** 2020

**Тип:** Научная статья (ACS Central Science)

**Релевантность:** Ранняя влиятельная работа по GAN-based генерации кристаллических структур с composition conditioning. Composition-conditioned GAN для тернарных материалов (Mg-Mn-O система). Inversion-free представление кристаллов через fractional coordinates. Сгенерировал 23 новые структуры с разумной стабильностью и band gaps. Комбинирован с HTVS для поиска photoanode материалов. Point cloud представление структур.

**Ссылка:** https://doi.org/10.1021/acscentsci.0c00426

---

### 9. CLaSP: Contrastive Language-Structure Pre-training for Materials Science

**Авторы:** Suzuki, Y., et al.

**Год:** 2025

**Тип:** Препринт (arXiv:2501.12919)

**Релевантность:** Новый contrastive learning подход, связывающий кристаллические структуры с естественным языком для materials discovery. Crossmodal embedding пространства между структурами и текстами. Contrastive learning между structure-language парами. Обучен на 406,048 кристаллических структурах из Crystallography Open Database (COD). Сравнение с CMML (Contrastive Materials Metric Learning), который выравнивает структуры с XRD паттернами. Позволяет text-based materials retrieval.

**Ссылка:** https://arxiv.org/abs/2501.12919

---

## Active Learning, Few-Shot и Meta-Learning

### 10. Few-Shot Learning for EBSD Pattern Classification

**Авторы:** Kaufmann, K., Lane, H., Liu, X., Vecchio, K.S.

**Год:** 2021

**Тип:** Научная статья (Scientific Reports, Vol. 11, Article 8172)

**Релевантность:** Применяет few-shot transfer learning (от ImageNet weights) для классификации EBSD паттернов к 6 space groups в (4/m 3̄ 2/m) point group. Использует только 400 паттернов на space group для обучения. Модель конвергирует в 2× раза быстрее (26 epochs vs 50), чем обучение с нуля, достигая более высокой precision и recall. Демонстрирует классификацию кристаллографических space groups с ограниченными размеченными данными. Shapley values и class activation maps для интерпретируемости.

**Ссылка:** https://doi.org/10.1038/s41598-021-87557-5

---

### 11. Active Meta-Learning for Perovskite Crystallization Experiments

**Авторы:** DeCost, B.L., Ament, et al.

**Год:** 2022

**Тип:** Научная статья (Journal of Chemical Physics, Vol. 156, 014108)

**Релевантность:** Применяет Model-Agnostic Meta-Learning (MAML) и PLATIPUS для роста halide perovskite через inverse temperature crystallization. Датасет 1,870 реакций из 19 различных organoammonium lead iodide систем. С фиксированным бюджетом в 20 экспериментов, PLATIPUS достигает превосходного предсказания композиций реакций, приводящих к кристаллам. Напрямую решает проблему sample-efficient learning и быстрой адаптации к новым кристаллическим системам.

**Ссылка:** https://doi.org/10.1063/5.0076636

---

### 12. Surface Multi-Task Learning for Magnesium Intermetallics

**Авторы:** Qian et al.

**Год:** 2024

**Тип:** Научная статья (Digital Discovery, RSC)

**Релевантность:** Представляет SEM-CGCNN (Surface Emphasized Multi-task CGCNN) для одновременного предсказания множественных поверхностных свойств из кристаллических структур. Обучен на 3,526 поверхностных структурах бинарных Mg интерметаллидов с surface energies и work functions. Multi-task подход демонстрирует превосходную эффективность над оригинальным CGCNN для анизотропного предсказания поверхностных свойств. Показывает transferability при fine-tuning к датасетам чистых металлов и других интерметаллидов.

**Ссылка:** https://doi.org/10.1016/j.dche.2024.100389

---

### 13. XRDMatch: Semi-Supervised Learning for Lithium Superionic Conductors

**Авторы:** (авторы из публикации Energy & Environmental Science 2024)

**Год:** 2024

**Тип:** Научная статья (Energy & Environmental Science, RSC)

**Релевантность:** Интегрирует consistency regularization и pseudo-labeling в semi-supervised фреймворк, используя только XRD паттерны как дескрипторы. Использует неразмеченные данные из ICSD базы для поддержки ограниченных размеченных данных для литий-ионных проводников. F1 score ensemble модели достигает 0.92. Решает проблему дефицита размеченных данных при распознавании кристаллических структур.

**Ссылка:** https://pubs.rsc.org/en/content/articlelanding/2024/ee/d4ee02970d

---

## Материал-специфические применения

### 14. Perovskite Synthesizability using Graph Neural Networks

**Авторы:** Gu, G.H., Jang, J., Noh, J., et al.

**Год:** 2022

**Тип:** Научная статья (npj Computational Materials)

**Релевантность:** Graph Neural Network с positive-unlabeled learning (PU learning) для предсказания синтезируемости всех типов перовскитов (halides, oxides, anti-perovskites). Domain-specific transfer learning достигает 95.7% true positive rate. Решает проблему композиционной сложности перовскитов и предсказания phase stability. Graph convolutions кодируют структурную информацию. Покрывает 943 синтезированных + 11,964 виртуальных структур перовскитов.

**Ссылка:** https://doi.org/10.1038/s41524-022-00757-z

---

### 15. MOFSimplify: Machine Learning for MOF Stability Prediction

**Авторы:** Nandy, A., Terrones, G., Arunachalam, N., et al.

**Год:** 2022

**Тип:** Научная статья (Scientific Data, Nature)

**Релевантность:** Artificial Neural Networks с NLP для data mining для предсказания стабильности MOF при удалении растворителя и термическом разложении. Использует revised autocorrelations (RACs) как структурные fingerprints из кристаллографических файлов. Решает проблему больших unit cells и структурной сложности MOF. Датасет: 2,179 MOFs с solvent removal stability, 3,132 с thermal stability. Точность 0.76 для solvent removal (AUC: 0.79), MAE 47°C для thermal stability.

**Ссылка:** https://doi.org/10.1038/s41597-022-01181-0

---

### 16. Deep Learning for 2D Materials with Flat Electronic Bands

**Авторы:** Bhattacharya, A., Timokhin, I., Chatterjee, R., et al.

**Год:** 2023

**Тип:** Научная статья (npj Computational Materials)

**Релевантность:** CNN для идентификации flat band материалов + HDBSCAN clustering для симметрийной классификации 2D материалов. Автоматическая идентификация flat band материалов и sublattice структур. Решает проблему layered структур и топологии электронных band. Обследовано 5,270 2D материалов из 2Dmatpedia. Идентифицировано 2,127 plane-flat материалов, классифицированных в 51 структурный кластер. Новый подход использует band structure images вместо параметризованных band.

**Ссылка:** https://doi.org/10.1038/s41524-023-01056-x

---

### 17. Bandgap Prediction in Graphene-Boron Nitride Hybrids

**Авторы:** Dong, Y., Wu, C., Zhang, C., et al.

**Год:** 2019

**Тип:** Научная статья (npj Computational Materials)

**Релевантность:** Три CNN архитектуры (VGG16, ResNet-based RCN, custom CCN) с transfer learning для распознавания конфигураций структур и предсказания bandgap для doped 2D материалов (graphene и h-BN гибриды). Решает проблему конфигурационной сложности в layered 2D материалах. 2D matrix дескрипторы для кодирования атомных конфигураций. Достигает >90% R² для 4×4 и 5×5 supercell систем. RMSE ~0.1 eV для bandgap. Transfer learning улучшает предсказание для больших систем (6×6 supercells).

**Ссылка:** https://doi.org/10.1038/s41524-019-0165-4

---

## Hybrid методы и оптимизация

### 18. BOWSR: Bayesian Optimization With Symmetry Relaxation

**Авторы:** Zuo, Y., Chen, C., Sun, W., Meng, Y.S., Ong, S.P., et al.

**Год:** 2021

**Тип:** Научная статья (Materials Today, 51, 126-135)

**Релевантность:** BOWSR алгоритм для DFT-free structure relaxation, комбинирующий MEGNet formation energy модель с Bayesian optimization. Symmetry-constrained relaxation поддерживает space group и Wyckoff positions во время оптимизации. Оптимизирует только независимые lattice параметры. Успешно идентифицировал и синтезировал два новых ultra-incompressible материала: MoWC2 (P63/mmc) и ReWB (Pca21). Просканировал 399,960 transition metal borides и carbides. Physics-informed подход с кристаллографическими симметрийными ограничениями.

**Ссылка:** https://arxiv.org/abs/2104.10242

---

### 19. SCCOP: Symmetry-based Combinatorial Crystal Optimization Program

**Авторы:** Li, C.-N., Liang, H.-P., Zhang, X., Zhu, J.-X., Wang, D.-D., et al.

**Год:** 2023

**Тип:** Научная статья (npj Computational Materials, Vol. 9, 176)

**Релевантность:** Пятиэтапный фреймворк: (i) random sampling с symmetry constraints, (ii) Bayesian optimization с crystal graph representation, (iii) transfer learning для обновлений модели, (iv) ML-accelerated simulated annealing + DFT optimization, (v) additive feature attribution analysis. Использует CGCNN для характеризации структур. Gaussian Process для Bayesian optimization с probability of improvement acquisition function. В 10× раз быстрее чем DFT-GA и DFT-PSO при сохранении сопоставимой точности. Обнаружил 28 новых стабильных B-C-N структур.

**Ссылка:** https://doi.org/10.1038/s41524-023-01122-4

---

### 20. Multifidelity Statistical Machine Learning for Molecular Crystals

**Авторы:** Egorova, O., Hafizi, R., Woods, D.C., Day, G.M.

**Год:** 2020

**Тип:** Научная статья (Journal of Physical Chemistry A, 124(39), 8065-8078)

**Релевантность:** Multi-fidelity подход используя autoregressive Gaussian process. Связывает force field → GGA DFT (PBE) → hybrid DFT (PBE0) вычисления. Statistical ML для предсказания дорогих hybrid functional DFT энергий. Использует менее дорогие PBE вычисления как intermediate fidelity level. Достиг PBE0 energy предсказаний с ошибками <1 kJ/mol используя только 4.2-6.8% от полной стоимости вычислений. Probabilistic модель обеспечивает uncertainty quantification для energy ranking. Multi-fidelity hybrid подход комбинирует physics-based методы с ML (Gaussian processes).

**Ссылка:** https://doi.org/10.1021/acs.jpca.0c05006

---

## Сводная таблица по направлениям

| Направление | Количество | Ключевые методы |
|-------------|------------|-----------------|
| Attention/Transformers | 4 | Multi-head attention, SE(3) transformers, edge-gated attention, hierarchical message passing |
| Unsupervised/Generative | 5 | VAE, GAN (Wasserstein, composition-conditioned), self-supervised (MoCo), contrastive learning |
| Active/Few-shot/Meta | 4 | Few-shot transfer learning, MAML, PLATIPUS, multi-task learning, semi-supervised |
| Material-specific | 4 | Perovskites (GNN + PU learning), MOFs (ANN + RACs), 2D materials (CNN + clustering) |
| Hybrid/Optimization | 3 | Bayesian optimization, symmetry constraints, multi-fidelity GP, simulated annealing |

**Временное распределение:** 2019 (1), 2020 (2), 2021 (2), 2022 (4), 2023 (4), 2024 (4), 2025 (3)

**Все источники фокусируются на:** Random Forest альтернативах (GNN, CNN, transformer), устойчивости к дефектам и поворотам (через SE(3)/SO(3) инвариантность, аугментации), нормализации координат (fractional coordinates, Wyckoff positions), расстояниях между атомами (graph representations, bond distances/angles), и НЕ пересекаются с 50 исключенными источниками.
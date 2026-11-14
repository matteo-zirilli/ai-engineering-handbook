# Data used in Part III

`housing.csv` — 545 house sales, 13 columns. Byte-identical copy (MD5
`801f8030dad1df22a53edfdbfa4e80f0`) of `Housing.csv` from the Kaggle dataset
"Housing Prices Dataset" by M Yasser H (2021), released there under
**CC0: Public Domain**. The records originate from the sample of 546 houses
sold in Windsor (Ontario, Canada) in 1987 published by Anglin and Gençay
(1996, *Journal of Applied Econometrics* 11(6), 633–648; replication data in
the JAE Data Archive, doi:10.15456/jae.2022313.1255545048): in the Kaggle file
prices are multiplied by 70, one sale is missing, columns are renamed
(`lotsize` → `area`, `driveway` → `mainroad`, `recroom` → `guestroom`,
`fullbase` → `basement`, `gashw` → `hotwaterheating`, `airco` →
`airconditioning`, `garagepl` → `parking`) and a `furnishingstatus` column of
undocumented origin is added. The check is executed in the project chapter of
Part III (`ml/08-project-real-estate.qmd`; the folder name starts with `_` so that Quarto does not render this file).

The other datasets of Part III are generated in the code or ship with
scikit-learn (`load_breast_cancer`, `load_wine`; UCI Machine Learning
Repository, CC BY 4.0).

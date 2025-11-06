[[+Home]] %% tags:: #MOC #mmss/moc %%

# MMSS Systems MOC
**Meta-Mind System Structure** - коллекция всех версий систем MMSS.
```meta-bind-button
label: CREATE
icon: ""
style: default
class: ""
cssStyle: ""
tooltip: "1"
id: create-mmss-system
hidden: false
actions:
  - type: templaterCreateNote
    templateFile: Extras/Templates/Template, MMSS System.md
    folderPath: MMSS/Systems
    fileName: TKTK
    openNote: true
    openIfAlreadyExists: false

```

```dataview
TABLE 
  technical-version as "Версия",
  choice(entropy = 0, "⭐", "📊") as "Стаб",
  formula-count as "Формулы",
  quality-score as "Качество",
  file.ctime as "Создана"
FROM "MMSS/Systems" and -#MOC
SORT file.ctime DESC
```
```dataview
TABLE WITHOUT ID
  "📈 " + length(rows) as "Всего систем",
  round(avg(entropy), 3) as "Средняя энтропия",
  round(avg(quality-score), 2) as "Среднее качество",
  round(avg(formula-count)) as "Среднее кол-во формул"
FROM #mmss/system and -#MOC
```
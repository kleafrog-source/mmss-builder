[[+Home]] %% tags:: #MOC %%

# MMSS Systems MOC

**Template:** [[Template, MMSS System]]

```meta-bind-button
label: Новая MMSS Система
icon: "plus"
style: primary
class: ""
tooltip: "Создать новую MMSS систему"
id: "create-mmss-system"
hidden: false
actions:
  - type: templaterCreateNote
    templateFile: "Extras/Templates/Template, MMSS System.md"
    folderPath: "MMSS/Systems"
    fileName: "TKTK"
    openNote: true
    openIfAlreadyExists: false
    
 ```
 ```dataview   
TABLE 
  technicalversion as "Версия",
  choice(entropy = 0, "⭐", "📊") as "Стаб",
  formulacount as "Формулы",
  qualityscore as "Качество",
  file.ctime as "Создана"
FROM "MMSS/Systems" and -#MOC
SORT file.ctime DESC
```
```dataview 
TABLE WITHOUT ID
  "📈 " + length(rows) as "Всего систем",
  round((entropy), 3) as "Средняя энтропия", 
  round((qualityscore), 2) as "Среднее качество",
  round((formulacount)) as "Среднее кол-во формул"
FROM #mmss/system and -#MOC
```
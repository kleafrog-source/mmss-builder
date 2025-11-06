[[+Home]] %% tags:: #MOC #mmss/moc %%

# MMSS Systems MOC

```meta-bind-button
label: 🚀 Новая MMSS Система
icon: "rocket"
style: primary
class: "mmss-create-button"
tooltip: "Создать новую MMSS систему"
id: "create-mmss-system"
hidden: false
actions:
  - type: templaterCreateNote
    templateFile: "Extras/Templates/Template, MMSS Syst.md"
    folderPath: "MMSS/Systems"
    fileName: "TKTK System Name"
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


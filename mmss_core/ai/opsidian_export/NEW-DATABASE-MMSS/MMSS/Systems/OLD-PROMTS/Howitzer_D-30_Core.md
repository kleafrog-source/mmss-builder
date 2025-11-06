{
  "Howitzer_D-30_MMSS_Full_Detail": {
    "root": {
      "id": "Howitzer_D-30_Core",
      "label": "Гаубица 122-мм Д-30",
      "description": "Детальная MMSS модель гаубицы Д-30 с размерами всех компонентов вплоть до винтиков",
      "components": [
        {
          "id": "Barrel",
          "label": "Ствол",
          "dimensions": {
            "length_total_m": 4.66,
            "length_tube_m": 4.3,
            "caliber_m": 0.122,
            "number_of_rifling_grooves": 36,
            "rifling_length_m": 3.4,
            "muzzle_brake_length_m": 0.3
          },
          "meta_formulas": {
            "length_tube": "length_total - muzzle_brake_length",
            "rifling_length": "length_tube * 0.79",
            "caliber": "0.122"
          },
          "subcomponents": [
            {
              "id": "Breech",
              "label": "Затвор клиновой",
              "dimensions": {
                "width_m": 0.25,
                "height_m": 0.15,
                "thickness_m": 0.1
              },
              "meta_formulas": {
                "width": "caliber * 2",
                "height": "caliber * 1.25",
                "thickness": "caliber * 0.8"
              }
            },
            {
              "id": "Muzzle_brayke",
              "label": "Дульный тормоз",
              "dimensions": {
                "length_m": 0.3,
                "diameter_m": 0.28
              },
              "meta_formulas": {
                "length": "0.3",
                "diameter": "caliber * 2.25"
              }
            }
          ]
        },
        {
          "id": "Recoil_System",
          "label": "Откатная система",
          "dimensions": {
            "recoil_length_m_min": 0.74,
            "recoil_length_m_max": 0.93,
            "recoil_fluid_volume_liters": 10.3
          },
          "meta_formulas": {
            "recoil_length_avg": "(recoil_length_m_min + recoil_length_m_max) / 2"
          },
          "subcomponents": [
            {
              "id": "Hydropneumatic_Recoil",
              "label": "Гидропневматический гаубицы откатный механизм",
              "dimensions": {
                "length_m": 0.85
              },
              "meta_formulas": {
                "length": "recoil_length_avg"
              }
            }
          ]
        },
        {
          "id": "Carriage",
          "label": "Лафет",
          "dimensions": {
            "width_operational_m": 5.6,
            "length_transport_m": 5.4,
            "width_transport_m": 2.2,
            "height_transport_m": 1.8,
            "wheel_diameter_m": 0.8,
            "ground_clearance_m": 0.325,
            "legs_count": 3
          },
          "meta_formulas": {
            "width_operational": "length_transport * 1.037",
            "wheel_diameter": "0.8",
            "ground_clearance": "0.325"
          },
          "subcomponents": [
            {
              "id": "Wheel",
              "label": "Колесо",
              "dimensions": {
                "diameter_m": 0.8,
                "width_m": 0.2
              },
              "meta_formulas": {
                "diameter": "wheel_diameter",
                "width": "diameter * 0.25"
              }
            },
            {
              "id": "Leg",
              "label": "Нога лафета",
              "dimensions": {
                "length_m": 2.0,
                "width_m": 0.15,
                "thickness_m": 0.12
              },
              "meta_formulas": {
                "length": "width_operational / legs_count",
                "width": "length_m * 0.075",
                "thickness": "width * 0.8"
              }
            }
          ]
        },
        {
          "id": "Sights",
          "label": "Прицельные устройства",
          "dimensions": {
            "panoramic_sight_length_m": 0.5,
            "telescopic_sight_length_m": 0.7
          },
          "meta_formulas": {
            "panoramic_sight_length": "0.5",
            "telescopic_sight_length": "0.7"
          }
        },
        {
          "id": "Small_Parts",
          "label": "Мелкие детали (винты, гайки, крепеж)",
          "dimensions": {
            "typical_screw_length_mm": 20,
            "typical_screw_diameter_mm": 4,
            "typical_nut_diameter_mm": 8
          },
          "meta_formulas": {
            "typical_screw_length": "0.02",
            "typical_screw_diameter": "0.004",
            "typical_nut_diameter": "0.008"
          },
          "description": "Размеры мелких крепежных деталей, типовых винтов и гаек для сборки"
        }
      ]
    }
  }
}

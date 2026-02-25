```bash
/sphenix/tg/tg01/commissioning/CaloCalibWG/sli/fm4npp_eval/d9_m5_k30_p20_eval_merged_d70000_1_seed10_per_point_data.csv
/sphenix/tg/tg01/commissioning/CaloCalibWG/sli/fm4npp_eval/d9_m5_k30_p20_eval_merged_d70000_1_seed1_per_point_data.csv
/sphenix/tg/tg01/commissioning/CaloCalibWG/sli/fm4npp_eval/d9_m5_k30_p20_eval_merged_d70000_1_seed2_per_point_data.csv
/sphenix/tg/tg01/commissioning/CaloCalibWG/sli/fm4npp_eval/d9_m5_k30_p20_eval_merged_d70000_1_seed3_per_point_data.csv
/sphenix/tg/tg01/commissioning/CaloCalibWG/sli/fm4npp_eval/d9_m5_k30_p20_eval_merged_d70000_1_seed4_per_point_data.csv
/sphenix/tg/tg01/commissioning/CaloCalibWG/sli/fm4npp_eval/d9_m5_k30_p20_eval_merged_d70000_1_seed5_per_point_data.csv
/sphenix/tg/tg01/commissioning/CaloCalibWG/sli/fm4npp_eval/d9_m5_k30_p20_eval_merged_d70000_1_seed6_per_point_data.csv
/sphenix/tg/tg01/commissioning/CaloCalibWG/sli/fm4npp_eval/d9_m5_k30_p20_eval_merged_d70000_1_seed7_per_point_data.csv
/sphenix/tg/tg01/commissioning/CaloCalibWG/sli/fm4npp_eval/d9_m5_k30_p20_eval_merged_d70000_1_seed8_per_point_data.csv
/sphenix/tg/tg01/commissioning/CaloCalibWG/sli/fm4npp_eval/d9_m5_k30_p20_eval_merged_d70000_1_seed9_per_point_data.csv
```

```bash
python point_to_track.py \
--input /sphenix/tg/tg01/commissioning/CaloCalibWG/sli/fm4npp_eval/d9_m5_k30_p20_eval_merged_d70000_1_seed1_per_point_data.csv \
--output /sphenix/user/hwyu/calotrack_tree/macro/dedx-fm/seed1_per_track.csv
```

```bash
python infer_pid_mapping.py --input /sphenix/tg/tg01/commissioning/CaloCalibWG/sli/fm4npp_eval/d9_m5_k30_p20_eval_merged_d70000_1_seed1_per_point_data.csv
```
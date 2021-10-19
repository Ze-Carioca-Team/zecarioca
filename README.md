# ZeCarioca

process synthetic dialogs
``` sh
python processdialog.py --file synthetic_backtranslation_deanonymization.json
```


fine tune to synthetic
``` sh
python finetune.py --checkpoint models/adrenaline_multiwoz/epoch56_trloss0.40_gpt2 --train_file data/process.train.json --validation_file data/process.valid.json --batch_size 4 --gradient_accumulation_steps 16
```

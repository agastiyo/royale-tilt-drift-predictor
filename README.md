# royale-tilt-drift-predictor
A data-to-insight pipeline that ingests RoyaleAPI battle logs, builds time-ordered sequences with engineered “session” and “deck” features, and trains a GRU/LSTM/Transformer to predict the next-match win probability while quantifying short-term tilt and longer-term performance drift.

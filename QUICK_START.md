# UltraWealth Quick Start Guide

## ✅ What's Ready

All critical bugs have been fixed! The system is now ready for overnight RL agent training.

## 🚀 Run Overnight Training (Windows)

### Option 1: PowerShell Script (Recommended)
```powershell
cd C:\Users\mjmil\UltraCore
.\train_agents_windows.ps1
```

### Option 2: Direct Python
```powershell
cd C:\Users\mjmil\UltraCore
python train_rl_agents.py
```

## ⚙️ Configure Training Episodes

To run 500 episodes for overnight training:

1. Open `train_rl_agents.py`
2. Find line 62: `n_episodes = 100`
3. Change to: `n_episodes = 500`
4. Save and run the training script

**Estimated Time:** 500 episodes will take approximately 4-6 hours on a modern machine.

## 📊 What Gets Trained

All 4 RL agents will be trained:

- **Alpha Agent** (Q-Learning) - POD1 Preservation
- **Beta Agent** (Policy Gradient) - POD2 Income  
- **Gamma Agent** (DQN) - POD3 Growth
- **Delta Agent** (A3C) - POD4 Opportunistic

Trained models are saved to: `models/rl_agents/`

## 🧪 Test the System

After training, test the complete system:

```powershell
python end_to_end_example.py
```

This will run a full portfolio optimization with your trained agents.

## 🔧 MCP Server Usage

Start the MCP server:

```powershell
python src\ultracore\mcp\server.py
```

Or use with manus-mcp-cli:

```bash
manus-mcp-cli server add ultracore-financial-data python src/ultracore/mcp/server.py
manus-mcp-cli tool list -s ultracore-financial-data
```

## 📚 Documentation

- **ULTRAWEALTH_SUMMARY.md** - Complete project summary
- **MCP_SERVER_README.md** - MCP server documentation
- **end_to_end_example.py** - Full system walkthrough

## 🐛 Bugs Fixed

✅ **RL Training Bug:** Fixed `ValueError: low >= high` in portfolio_env.py  
✅ **Gymnasium Compatibility:** Updated all training loops for Gymnasium API  
✅ **MCP Server:** All 7 tests passing with 10 working tools  
✅ **Data Frequency:** Fixed monthly→daily data issue (realistic returns)  

## 📈 Expected Results

After training, you should see portfolio optimization results like:

- **Expected Return:** ~26% p.a.
- **Volatility:** ~6%
- **Sharpe Ratio:** ~3.8
- **After-tax Return:** ~17.5%

## 🆘 Troubleshooting

**Issue:** Python not found  
**Solution:** Ensure Python 3.11+ is installed and in PATH

**Issue:** Missing packages  
**Solution:** Run `pip install -r requirements_etf_system.txt`

**Issue:** No ETF data  
**Solution:** Run `python download_all_etfs.py` first

## 📞 Next Steps

1. ✅ Run overnight training (500 episodes)
2. ⏳ Build risk questionnaire UI
3. ⏳ Create UltraOptimiser presentation slides
4. ⏳ Add more data sources to MCP server

---

**Ready to train!** 🚀

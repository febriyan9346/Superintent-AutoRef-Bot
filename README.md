# Superintent.AI Auto Referral Bot

🔗 **[Join Superintent.AI](https://mission.superintent.ai/?referralCode=LZ3v477zNF)**

An automated referral bot for Superintent.AI that creates multiple accounts, binds referral codes, and performs daily check-ins.

## Features

- ✅ Automatic wallet generation
- ✅ Account creation and authentication
- ✅ Referral code binding
- ✅ Daily check-in automation
- ✅ Proxy support (optional)
- ✅ Detailed logging with timestamps
- ✅ Account data export
- ✅ Multi-account management

## Requirements

- Python 3.7+
- Required packages (see `requirements.txt`)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/febriyan9346/Superintent-AutoRef-Bot.git
cd Superintent-AutoRef-Bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage (Without Proxy)

1. Run the bot:
```bash
python bot.py
```

2. Enter your referral code when prompted
3. Enter the number of referral accounts to create
4. Select option `2` for running without proxy

### Advanced Usage (With Proxy)

1. Create a `proxy.txt` file in the project directory
2. Add your proxies (one per line) in any of these formats:
   ```
   ip:port
   ip:port:username:password
   username:password@ip:port
   http://username:password@ip:port
   socks5://username:password@ip:port
   ```

3. Run the bot:
```bash
python bot.py
```

4. Enter your referral code
5. Enter the number of accounts to create
6. Select option `1` to use proxies

## Output Files

The bot creates two files to store account information:

- `referral_accounts.txt` - Contains private keys of created accounts
- `referral_accounts_details.txt` - Contains detailed information (address, private key, proxy used)

**⚠️ IMPORTANT: Keep these files secure and never share your private keys!**

## Proxy Format Examples

```
# Format 1: IP:Port
192.168.1.1:8080

# Format 2: IP:Port:Username:Password
192.168.1.1:8080:user:pass

# Format 3: Username:Password@IP:Port
user:pass@192.168.1.1:8080

# Format 4: With Protocol
http://user:pass@192.168.1.1:8080
socks5://user:pass@192.168.1.1:8080
```

## Features Breakdown

### Account Creation
- Generates random Ethereum wallets
- Signs authentication messages
- Binds referral codes automatically

### Daily Check-in
- Checks if already completed
- Performs check-in automatically
- Reports earned points

### Stats Tracking
- Displays total points
- Shows account status
- Logs all activities

## Logging

The bot provides colored console output for easy monitoring:
- 🔵 **INFO** - General information
- 🟢 **SUCCESS** - Successful operations
- 🔴 **ERROR** - Errors and failures
- 🟡 **WARNING** - Warnings
- 🟣 **CYCLE** - Account processing status

## Troubleshooting

### Common Issues

1. **Login Failed**
   - Check your internet connection
   - Verify proxy settings if using proxies
   - Try running without proxy

2. **Referral Code Invalid**
   - Ensure you entered the correct referral code
   - Check for extra spaces

3. **Proxy Errors**
   - Verify proxy format in `proxy.txt`
   - Test proxies individually
   - Try running without proxy first

## Disclaimer

This bot is for educational purposes only. Use it responsibly and at your own risk. The authors are not responsible for any misuse or violations of the Superintent.AI terms of service.

## Support Us with Cryptocurrency

You can make a contribution using any of the following blockchain networks:

| Network | Wallet Address |
|---------|---------------|
| **EVM** | `0x216e9b3a5428543c31e659eb8fea3b4bf770bdfd` |
| **TON** | `UQCEzXLDalfKKySAHuCtBZBARCYnMc0QsTYwN4qda3fE6tto` |
| **SOL** | `9XgbPg8fndBquYXkGpNYKHHhymdmVhmF6nMkPxhXTki` |
| **SUI** | `0x8c3632ddd46c984571bf28f784f7c7aeca3b8371f146c4024f01add025f993bf` |

## Author

**FEBRIYAN**

## License

This project is open source and available under the MIT License.

---

⭐ If you find this bot helpful, please star the repository!

🐛 Found a bug? Open an issue on GitHub.

💡 Have a feature request? Feel free to suggest it!
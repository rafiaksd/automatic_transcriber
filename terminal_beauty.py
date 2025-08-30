from pyfiglet import Figlet
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--font', type=str, help='Name of the font')

args = parser.parse_args()

print(f"ARGS GOT : {args.font}")
figlet = Figlet(font=args.font)
print(figlet.renderText('gpt-oss:20b'))
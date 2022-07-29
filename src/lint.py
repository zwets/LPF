import argparse
import logging
from pylint.lint import Run

logging.getLogger().setLevel(logging.INFO)

parser = argparse.ArgumentParser(prog="LINT")

parser.add_argument('-p',
                    '--path',
                    help='path to directory you want to run pylint | '
                         'Default: %(default)s | '
                         'Type: %(type)s ',
                    default='./src',
                    type=str)

args = parser.parse_args()
path = str(args.path)
threshold = 0 #0 all ways pass, set to 10 eventually

logging.info('PyLint Starting | '
             'Path: {} | '
             'Threshold: {} '.format(path, threshold))

results = Run([path], do_exit=False)


final_score = results.linter.stats['global_note']

logging.info('FINAL SCORE: {} '.format(final_score))


if final_score < threshold:

    message = ('PyLint Failed | '
               'Score: {} | '
               'Threshold: {} '.format(final_score, threshold))

    logging.error(message)
    raise Exception(message)

else:
    message = ('PyLint Passed | '
               'Score: {} | '
               'Threshold: {} '.format(final_score, threshold))

    logging.info(message)

    exit(0)

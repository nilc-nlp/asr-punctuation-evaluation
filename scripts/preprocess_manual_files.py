import os
import re

def preprocess_line(line, remove=["P/ 1", "RISO", "[P/1]", "[P/2]", "[P]", "[R]", "[P1]", "(RISOS)", "(RISO)", 
                                  "(risos)", 'P1 – ', 'R – ', 'P/1- ' 'R- ', 'P – ', 'P/1 – ', 
                                  'P/2 – ', 'P/1-', 'R- ', "(pausa)", '–', ')', '(']):
    line = line.rstrip()
    for x in remove:
        line = line.replace(x,'')

    line = line.replace("etc.", "etc")
    line = line.replace("...", '=')
    line = line.replace('”', '"')
    line = line.replace('“', '"')
    return line.strip()

def preprocess_dir(input_dir, 
                   output_dir, 
                   final_punctuation_marks=['.', '!', '?'],
                   replace_in_quotes=None,
                   remove_quotes=True,
                   split_on_quotes=False):
    files = list(filter(lambda f: f.endswith("txt"), os.listdir(input_dir)))
    for f in files:
        output_path = os.path.join(output_dir, f.replace(".txt", ''))
        os.makedirs(output_path, exist_ok=True)
        
        with open(f) as input_file:
            file_contents = input_file.read().replace('\u2028','\n').replace('\u2029','\n').splitlines()
        
        part = ''
        i = 1
        
        for line in file_contents:
            line = preprocess_line(line)
            if not line:
                continue
            part += ' ' + line
            if not part.rstrip().endswith(final_punctuation_marks):
                continue
            
            if part:
                with open(os.path.join(output_path, f"{i:04}.txt"), 'w') as pf:
                    i += 1
                    segments = []

                    if replace_in_quotes:
                        part = re.sub('".*?"', replace_in_quotes, part)
                    if remove_quotes:
                        part = part.replace('"', '')

                    if split_on_quotes:
                        segments += list(filter(lambda s: any(c.isalpha() or c.isdigit() for c in s), 
                                                re.findall('".*?"', part)))
                    # Split by punctuation
                    segments += list(filter(lambda s: any(c.isalpha() or c.isdigit() for c in s), 
                                            re.findall(f".*?[{final_punctuation_marks}]", part)))
                    
                    for s in segments:
                        s = s.replace("etc", "etc.")
                        s = s.replace("=", '...')
                        s = s.strip()
                        if s: 
                            print(s)
                            print(s, file=pf)
            
            part = ''

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser("Preprocess manual files")
    parser.add_argument('dir', type=str, help='Directory to preprocess')
    parser.add_argument('--output_dir', type=str, default='preprocessed_manual', help='Output directory')
    parser.add_argument('--final_punctuation_marks', type=str, default='.,!?;:', 
                        help='Final punctuation marks to create the segments. Use ".!?" to segment on sentences, '
                             'or ".!?,;:" to segment on any punctuation for punctuation analysis.')
    args = parser.parse_args()
    preprocess_dir(args.dir, args.output_dir, list(args.final_punctuation_marks))
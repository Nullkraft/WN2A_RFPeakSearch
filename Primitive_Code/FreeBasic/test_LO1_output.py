"""
    Testing my code agains Mike's default ADF4356 FreeBASIC reference code
    
    The unit_source_file.txt was created from a know good and tested  copy
    of Mike's working code.
"""

source_fname = "unit_test_source.txt"
generated_fname = "unit_test_generated.txt"


def compare_files(generated, source):
    A = open(generated, 'r')
    gen_file = A.readlines()

    B = open(source, 'r')
    src_file = B.readlines()
            
    if gen_file == src_file:
        print("\n"                                                 )
        print(" ==================================================")
        print(" ]                !!! Success !!!                 [")
        print(" ==================================================")
        print("\n"                                                 )
    else:
        print("\n"                                                 )
        print(" ==================================================")
        print(" ]                 !!! Fuck !!!                   [")
        print(" ==================================================")
        print("\n"                                                 )
    


if __name__ == '__main__':
    compare_files(generated_fname, source_fname)
    

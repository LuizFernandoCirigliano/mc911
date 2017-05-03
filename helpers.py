def print_error(type, lineno, error_msg):
    print("ERROR ({}) on line {}: {}".format(type, lineno, error_msg))


def get_data():
    import sys
    data = ""

    if len(sys.argv) == 1:
        # Test it out
        # data = '''
        # //3 + 4 * 10
        #   + -20 *2 ->
        #   ; [ ] =
        #   syn aba //oi
        #   // olarrrr
        #   oi
        #   /* linha ignorada
        #   "aaa"
        #   fim */
        #   a /* oooi */
        #   'x'
        #   "Hello world"
        #   /* oie \n */
        #   aa a
        #   '\a'
        #   a
        #   "DCL"
        #   /*DCL*/
        # '''
        data = bin_op_data


    return data

bin_op_data = "1 + 1"

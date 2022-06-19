class debug:
    def log(message:str, verbose:int=1, newline:bool=False):
        """ Print debug message """
        if not verbose:
            return

        message = f"\n{message}" if newline else message
        print(message)

    def separate(verbose:int=1):
        """ Print separator """
        if not verbose:
            return
        
        print("\n================\n")
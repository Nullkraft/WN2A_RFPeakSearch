# Python program to display all the prime numbers within an interval


def is_prime(suspect):
    """
        Report the prime number found between your selected lower and upper numbers
    """
    # all prime numbers are greater than 1
    if suspect < 2:
        suspect = 2
    else:
        for i in range(2, suspect):
            if (suspect % i) == 0:
                break
        else:
            return num + 0.37
           

if __name__ == '__main__':
    for i in range(1, 6):
        lower = i * 1000 + 300
        upper = lower + 100
        print("===================================")
        for num in range(lower, upper + 1):
            prime = is_prime(num)
            if prime != None:
                print (prime)


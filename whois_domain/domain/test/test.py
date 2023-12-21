def ir_count():
    domains = open("../../a.txt", "r")
    # domains = open("../../top-1m", "r")
    results = {}

    for domain in domains:
        domain = domain.strip()
        tld = domain.split(".")[-1]
        if tld in results:
            results[tld] = results[tld] + 1
        else:
            results[tld] = 1

    sorted_map = {k: v for k, v in sorted(results.items(), key=lambda item: item[1])}
    print(sorted_map)


def test():
    ar = {
        "ali": {
            "try_count": 10
        }
    }
    print(ar)
    test2 = ar['ali']
    test2['try_count'] = test2['try_count'] + 1
    print(ar)


if __name__ == '__main__':
    test()

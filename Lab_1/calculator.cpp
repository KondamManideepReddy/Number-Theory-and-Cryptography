#include <iostream>
#include <string>
#include <cstdlib>
#include <cstdint>

using namespace std;

class BigInt {
public:
    static const int N = 40; // 40*32 = 1280 bits
    uint32_t w[N];

    BigInt() { clear(); }

    void clear() {
        for (int i = 0; i < N; ++i) w[i] = 0;
    }

    bool isZero() const {
        for (int i = 0; i < N; ++i)
            if (w[i] != 0) return false;
        return true;
    }

    bool isOdd() const { return (w[0] & 1u) != 0; }

    void setUInt(uint32_t x) {
        clear();
        w[0] = x;
    }

    bool setDecimal(const string& s) {
        clear();
        if (s.size() == 0) return false;

        int start = 0;
        if (s[0] == '+') start = 1;
        if (start == (int)s.size()) return false;

        for (int i = start; i < (int)s.size(); ++i) {
            char c = s[i];
            if (c < '0' || c > '9') return false;
            mulSmall(10);
            if (!addSmall((uint32_t)(c - '0'))) return false;
        }
        return true;
    }

    string toDecimal() const {
        if (isZero()) return "0";

        BigInt t = *this;
        char rev[500];
        int len = 0;

        while (!t.isZero()) {
            uint32_t r = t.divSmall(10);
            rev[len++] = (char)('0' + r);
        }

        string out;
        for (int i = len - 1; i >= 0; --i)
            out.push_back(rev[i]);
        return out;
    }

    void mulSmall(uint32_t m) {
        uint64_t carry = 0;
        for (int i = 0; i < N; ++i) {
            uint64_t z = (uint64_t)w[i] * m + carry;
            w[i] = (uint32_t)z;
            carry = z >> 32;
        }
    }

    bool addSmall(uint32_t x) {
        uint64_t carry = x;
        for (int i = 0; i < N && carry != 0; ++i) {
            uint64_t z = (uint64_t)w[i] + carry;
            w[i] = (uint32_t)z;
            carry = z >> 32;
        }
        return carry == 0;
    }

    uint32_t divSmall(uint32_t d) {
        uint64_t rem = 0;
        for (int i = N - 1; i >= 0; --i) {
            uint64_t cur = (rem << 32) | w[i];
            w[i] = (uint32_t)(cur / d);
            rem = cur % d;
        }
        return (uint32_t)rem;
    }

    int compare(const BigInt& b) const {
        for (int i = N - 1; i >= 0; --i) {
            if (w[i] < b.w[i]) return -1;
            if (w[i] > b.w[i]) return 1;
        }
        return 0;
    }

    void add(const BigInt& b) {
        uint64_t carry = 0;
        for (int i = 0; i < N; ++i) {
            uint64_t z = (uint64_t)w[i] + b.w[i] + carry;
            w[i] = (uint32_t)z;
            carry = z >> 32;
        }
    }

    // Requires *this >= b.
    void subtract(const BigInt& b) {
        uint64_t borrow = 0;

        for (int i = 0; i < N; ++i) {
            uint64_t bi = (uint64_t)b.w[i] + borrow;

            if ((uint64_t)w[i] >= bi) {
                w[i] = (uint32_t)((uint64_t)w[i] - bi);
                borrow = 0;
            } else {
                w[i] = (uint32_t)(((uint64_t)1 << 32) +
                                  (uint64_t)w[i] - bi);
                borrow = 1;
            }
        }
    }

    int bitLength() const {
        for (int i = N - 1; i >= 0; --i) {
            if (w[i] != 0) {
                uint32_t x = w[i];
                int bits = 0;
                while (x != 0) {
                    x >>= 1;
                    ++bits;
                }
                return i * 32 + bits;
            }
        }
        return 0;
    }

    int getBit(int p) const {
        if (p < 0 || p >= N * 32) return 0;
        return (int)((w[p / 32] >> (p % 32)) & 1u);
    }

    void setBit(int p) {
        if (p < 0 || p >= N * 32) return;
        w[p / 32] |= (uint32_t)1u << (p % 32);
    }

    void shiftLeftOne() {
        uint32_t carry = 0;
        for (int i = 0; i < N; ++i) {
            uint32_t next = w[i] >> 31;
            w[i] = (w[i] << 1) | carry;
            carry = next;
        }
    }

    void shiftRightOne() {
        uint32_t carry = 0;
        for (int i = N - 1; i >= 0; --i) {
            uint32_t next = w[i] & 1u;
            w[i] = (w[i] >> 1) | (carry << 31);
            carry = next;
        }
    }
};

BigInt addNew(const BigInt& a, const BigInt& b) {
    BigInt r = a;
    r.add(b);
    return r;
}

BigInt subNew(const BigInt& a, const BigInt& b) {
    BigInt r = a;
    r.subtract(b);
    return r;
}

/* Schoolbook multiplication, implemented manually. */
BigInt multiply(const BigInt& a, const BigInt& b) {
    BigInt r;

    for (int i = 0; i < BigInt::N; ++i) {
        uint64_t carry = 0;

        for (int j = 0; j + i < BigInt::N; ++j) {
            uint64_t z = (uint64_t)a.w[i] * b.w[j]
                       + r.w[i + j] + carry;

            r.w[i + j] = (uint32_t)z;
            carry = z >> 32;
        }

        if (i < BigInt::N && i + (BigInt::N - i) < BigInt::N) {
            // never reached
        }
    }

    return r;
}

/*
   Binary long division:
   A = Q*B + R, 0 <= R < B.
*/
void divMod(const BigInt& A, const BigInt& B,
            BigInt& Q, BigInt& R) {
    Q.clear();
    R.clear();

    if (B.isZero()) return;

    int n = A.bitLength();

    for (int i = n - 1; i >= 0; --i) {
        R.shiftLeftOne();

        if (A.getBit(i))
            R.addSmall(1);

        if (R.compare(B) >= 0) {
            R.subtract(B);
            Q.setBit(i);
        }
    }
}

BigInt gcd(BigInt a, BigInt b) {
    while (!b.isZero()) {
        BigInt q, r;
        divMod(a, b, q, r);
        a = b;
        b = r;
    }
    return a;
}

struct SignedBig {
    bool negative;
    BigInt value;

    SignedBig() : negative(false) {}

    void setUInt(uint32_t x) {
        negative = false;
        value.setUInt(x);
    }
};

void normalize(SignedBig& x) {
    if (x.value.isZero())
        x.negative = false;
}

SignedBig negateSigned(const SignedBig& a) {
    SignedBig r = a;
    if (!r.value.isZero())
        r.negative = !r.negative;
    return r;
}

SignedBig signedAdd(const SignedBig& a, const SignedBig& b) {
    SignedBig r;

    if (a.negative == b.negative) {
        r.negative = a.negative;
        r.value = addNew(a.value, b.value);
    } else {
        int c = a.value.compare(b.value);

        if (c >= 0) {
            r.negative = a.negative;
            r.value = subNew(a.value, b.value);
        } else {
            r.negative = b.negative;
            r.value = subNew(b.value, a.value);
        }
    }

    normalize(r);
    return r;
}

SignedBig signedSubtract(const SignedBig& a, const SignedBig& b) {
    return signedAdd(a, negateSigned(b));
}

SignedBig signedMultiplyUnsigned(const BigInt& q,
                                 const SignedBig& x) {
    SignedBig r;
    r.negative = x.negative;
    r.value = multiply(q, x.value);
    normalize(r);
    return r;
}

/*
   Extended Euclidean algorithm:
   returns g,x,y such that ax + by = g.
*/
void extendedGCD(const BigInt& A, const BigInt& B,
                 BigInt& G, SignedBig& X, SignedBig& Y) {
    BigInt oldR = A;
    BigInt r = B;

    SignedBig oldS, s, oldT, t;
    oldS.setUInt(1);
    s.setUInt(0);
    oldT.setUInt(0);
    t.setUInt(1);

    while (!r.isZero()) {
        BigInt q, rem;
        divMod(oldR, r, q, rem);

        oldR = r;
        r = rem;

        SignedBig newS =
            signedSubtract(oldS, signedMultiplyUnsigned(q, s));
        oldS = s;
        s = newS;

        SignedBig newT =
            signedSubtract(oldT, signedMultiplyUnsigned(q, t));
        oldT = t;
        t = newT;
    }

    G = oldR;
    X = oldS;
    Y = oldT;
}

BigInt modulo(const BigInt& a, const BigInt& m) {
    BigInt q, r;
    divMod(a, m, q, r);
    return r;
}

BigInt one() {
    BigInt x;
    x.setUInt(1);
    return x;
}

BigInt modularAdd(const BigInt& a, const BigInt& b,
                  const BigInt& m) {
    BigInt x = modulo(a, m);
    BigInt y = modulo(b, m);

    x.add(y);
    return modulo(x, m);
}

BigInt modularMultiply(const BigInt& a, const BigInt& b,
                       const BigInt& m) {
    BigInt x = modulo(a, m);
    BigInt y = modulo(b, m);

    BigInt p = multiply(x, y);
    return modulo(p, m);
}

/*
   Square-and-multiply / repeated squaring.
*/
BigInt modularPowerFast(BigInt base, BigInt exponent,
                        const BigInt& modulus) {
    BigInt result = modulo(one(), modulus);
    base = modulo(base, modulus);

    while (!exponent.isZero()) {
        if (exponent.isOdd())
            result = modularMultiply(result, base, modulus);

        base = modularMultiply(base, base, modulus);
        exponent.shiftRightOne();
    }

    return result;
}

/*
   Naive modular exponentiation.
   Intended for timing comparison; it performs one modular
   multiplication for every increment of the exponent.
*/
BigInt modularPowerNaive(BigInt base, BigInt exponent,
                         const BigInt& modulus) {
    BigInt result = modulo(one(), modulus);
    base = modulo(base, modulus);

    BigInt oneValue = one();

    while (!exponent.isZero()) {
        result = modularMultiply(result, base, modulus);
        exponent.subtract(oneValue);
    }

    return result;
}

void printSigned(const SignedBig& x) {
    if (x.negative && !x.value.isZero())
        cout << "-";
    cout << x.value.toDecimal();
}

bool readBig(const char* s, BigInt& x) {
    return x.setDecimal(string(s));
}

bool readSignedBig(const char* s, BigInt& x, bool& negative) {
    if (s == nullptr || s[0] == '\0')
        return false;

    int start = 0;
    negative = false;

    if (s[0] == '-') {
        negative = true;
        start = 1;
    }
    else if (s[0] == '+') {
        start = 1;
    }

    // Only a sign was entered
    if (s[start] == '\0')
        return false;

    x.clear();

    for (int i = start; s[i] != '\0'; ++i) {
        char c = s[i];

        if (c < '0' || c > '9')
            return false;

        x.mulSmall(10);

        if (!x.addSmall((uint32_t)(c - '0')))
            return false;
    }

    // -0 should simply be 0
    if (x.isZero())
        negative = false;

    return true;
}

bool readBigMagnitude(const char* s, BigInt& x) {
    if (s == nullptr || s[0] == '\0')
        return false;

    int i = 0;

    // Ignore sign because GCD uses absolute values
    if (s[i] == '+' || s[i] == '-')
        i++;

    if (s[i] == '\0')
        return false;

    x.clear();

    for (; s[i] != '\0'; i++) {
        char c = s[i];

        if (c < '0' || c > '9')
            return false;

        x.mulSmall(10);

        if (!x.addSmall((uint32_t)(c - '0')))
            return false;
    }

    return true;
}

int main(int argc, char** argv) {
    if (argc < 2) {
        cout << "ERROR: missing operation\n";
        return 1;
    }

    string op = argv[1];

    if (op == "gcd" && argc == 4) {
    BigInt a, b;

    if (!readBigMagnitude(argv[2], a) ||
        !readBigMagnitude(argv[3], b)) {
        cout << "ERROR: invalid integer\n";
        return 2;
    }

    cout << gcd(a, b).toDecimal() << "\n";
    return 0;
}

    if (op == "egcd" && argc == 4) {
    BigInt a, b, g;
    SignedBig x, y;

    bool negativeA = false;
    bool negativeB = false;

    // Read signed inputs
    if (!readSignedBig(argv[2], a, negativeA) ||
        !readSignedBig(argv[3], b, negativeB)) {

        cout << "ERROR: invalid integer\n";
        return 2;
    }

    // Run Extended Euclid on positive magnitudes
    extendedGCD(a, b, g, x, y);

    /*
       We originally calculated:

           a_abs * x + b_abs * y = gcd

       But the actual inputs may be negative.

       If A was negative:
           A = -a_abs

       Therefore its coefficient must also change sign.
    */

    if (negativeA)
        x = negateSigned(x);

    if (negativeB)
        y = negateSigned(y);

    cout << "gcd=" << g.toDecimal() << "\n";

    cout << "x=";
    printSigned(x);
    cout << "\n";

    cout << "y=";
    printSigned(y);
    cout << "\n";

    return 0;
}

    if (op == "inverse" && argc == 4) {
        BigInt a, m, g;
        SignedBig x, y;

        if (!readBig(argv[2], a) || !readBig(argv[3], m)) return 2;

        if (m.isZero()) {
            cout << "ERROR: modulus cannot be zero\n";
            return 2;
        }

        extendedGCD(a, m, g, x, y);

        BigInt unity = one();

        if (g.compare(unity) != 0) {
            cout << "NO_INVERSE\n";
            return 0;
        }

        BigInt answer = modulo(x.value, m);

        if (x.negative && !answer.isZero()) {
            BigInt temp = m;
            temp.subtract(answer);
            answer = temp;
        }

        cout << answer.toDecimal() << "\n";
        return 0;
    }

    if (op == "modadd" && argc == 5) {
        BigInt a, b, m;
        if (!readBig(argv[2], a) ||
            !readBig(argv[3], b) ||
            !readBig(argv[4], m)) return 2;

        if (m.isZero()) {
            cout << "ERROR: modulus cannot be zero\n";
            return 2;
        }

        cout << modularAdd(a, b, m).toDecimal() << "\n";
        return 0;
    }

    if (op == "modmul" && argc == 5) {
        BigInt a, b, m;
        if (!readBig(argv[2], a) ||
            !readBig(argv[3], b) ||
            !readBig(argv[4], m)) return 2;

        if (m.isZero()) {
            cout << "ERROR: modulus cannot be zero\n";
            return 2;
        }

        cout << modularMultiply(a, b, m).toDecimal() << "\n";
        return 0;
    }

    if ((op == "powfast" || op == "pownaive") && argc == 5) {
        BigInt a, e, m;

        if (!readBig(argv[2], a) ||
            !readBig(argv[3], e) ||
            !readBig(argv[4], m)) return 2;

        if (m.isZero()) {
            cout << "ERROR: modulus cannot be zero\n";
            return 2;
        }

        if (op == "powfast")
            cout << modularPowerFast(a, e, m).toDecimal() << "\n";
        else
            cout << modularPowerNaive(a, e, m).toDecimal() << "\n";

        return 0;
    }

    cout << "ERROR: invalid operation or arguments\n";
    return 1;
}

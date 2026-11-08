
#include <mpi.h>

#include <algorithm>
#include <chrono>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <vector>

using namespace std;

using Matrix = vector<long long>;

void multiply_sequential(
    const Matrix &A,
    const Matrix &B,
    Matrix &C,
    int n)
{
    fill(C.begin(), C.end(), 0);

    for (int i = 0; i < n; i++)
    {
        for (int k = 0; k < n; k++)
        {
            for (int j = 0; j < n; j++)
            {
                C[static_cast<size_t>(i) * n + j] +=
                    A[static_cast<size_t>(i) * n + k] *
                    B[static_cast<size_t>(k) * n + j];
            }
        }
    }
}

int main(int argc, char *argv[])
{
    MPI_Init(&argc, &argv);

    int rank = 0;
    int process_count = 0;

    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &process_count);

    int n = 0;
    int valid = 1;

    Matrix A;
    Matrix B;
    Matrix C;

    double sequential_time = 0.0;

    if (rank == 0)
    {
        ifstream inA("A.txt");
        ifstream inB("B.txt");

        if (!inA || !inB)
        {
            cerr << "Cannot open input files\n";
            valid = 0;
        }
        else
        {
            int nA = 0;
            int nB = 0;

            if (!(inA >> nA) || !(inB >> nB) ||
                nA <= 0 || nA != nB)
            {
                cerr << "Invalid matrix sizes\n";
                valid = 0;
            }
            else if (
                static_cast<long long>(nA) * nA >
                numeric_limits<int>::max())
            {
                cerr << "Matrix is too large for MPI counts\n";
                valid = 0;
            }
            else
            {
                n = nA;

                size_t matrix_size =
                    static_cast<size_t>(n) * n;

                A.resize(matrix_size);
                B.resize(matrix_size);
                C.resize(matrix_size);

                for (size_t i = 0; i < matrix_size; i++)
                {
                    if (!(inA >> A[i]) || !(inB >> B[i]))
                    {
                        cerr << "Cannot read matrix elements\n";
                        valid = 0;
                        break;
                    }
                }
            }
        }

        if (valid)
        {
            Matrix sequential_C(
                static_cast<size_t>(n) * n, 0);

            auto start = chrono::steady_clock::now();

            multiply_sequential(A, B, sequential_C, n);

            auto finish = chrono::steady_clock::now();

            sequential_time =
                chrono::duration<double, milli>(
                    finish - start)
                    .count();
        }
    }

    MPI_Bcast(&valid, 1, MPI_INT, 0, MPI_COMM_WORLD);

    if (!valid)
    {
        MPI_Finalize();
        return 1;
    }

    MPI_Bcast(&n, 1, MPI_INT, 0, MPI_COMM_WORLD);

    if (rank != 0)
    {
        B.resize(static_cast<size_t>(n) * n);
    }

    int matrix_count = n * n;

    MPI_Bcast(
        B.data(),
        matrix_count,
        MPI_LONG_LONG_INT,
        0,
        MPI_COMM_WORLD);

    vector<int> send_counts(process_count);
    vector<int> send_displacements(process_count);

    vector<int> receive_counts(process_count);
    vector<int> receive_displacements(process_count);

    int base_rows = n / process_count;
    int remaining_rows = n % process_count;

    int current_displacement = 0;

    for (int i = 0; i < process_count; i++)
    {
        int rows = base_rows +
                   (i < remaining_rows ? 1 : 0);

        send_counts[i] = rows * n;
        send_displacements[i] = current_displacement;

        receive_counts[i] = rows * n;
        receive_displacements[i] = current_displacement;

        current_displacement += rows * n;
    }

    int local_rows = base_rows +
                     (rank < remaining_rows ? 1 : 0);

    Matrix local_A(
        static_cast<size_t>(local_rows) * n);

    Matrix local_C(
        static_cast<size_t>(local_rows) * n, 0);

    MPI_Barrier(MPI_COMM_WORLD);

    double start_time = MPI_Wtime();

    MPI_Scatterv(
        rank == 0 ? A.data() : nullptr,
        send_counts.data(),
        send_displacements.data(),
        MPI_LONG_LONG_INT,
        local_A.data(),
        local_rows * n,
        MPI_LONG_LONG_INT,
        0,
        MPI_COMM_WORLD);

    for (int i = 0; i < local_rows; i++)
    {
        for (int k = 0; k < n; k++)
        {
            for (int j = 0; j < n; j++)
            {
                local_C[static_cast<size_t>(i) * n + j] +=
                    local_A[static_cast<size_t>(i) * n + k] *
                    B[static_cast<size_t>(k) * n + j];
            }
        }
    }

    MPI_Gatherv(
        local_C.data(),
        local_rows * n,
        MPI_LONG_LONG_INT,
        rank == 0 ? C.data() : nullptr,
        receive_counts.data(),
        receive_displacements.data(),
        MPI_LONG_LONG_INT,
        0,
        MPI_COMM_WORLD);

    double local_time = MPI_Wtime() - start_time;
    double parallel_time = 0.0;

    MPI_Reduce(
        &local_time,
        &parallel_time,
        1,
        MPI_DOUBLE,
        MPI_MAX,
        0,
        MPI_COMM_WORLD);

    if (rank == 0)
    {
        ofstream out("C.txt");

        if (!out)
        {
            cerr << "Cannot create output file\n";
            MPI_Abort(MPI_COMM_WORLD, 1);
        }

        out << n << '\n';

        for (int i = 0; i < n; i++)
        {
            for (int j = 0; j < n; j++)
            {
                out << C[static_cast<size_t>(i) * n + j] << ' ';
            }

            out << '\n';
        }

        cout << "Matrix size: " << n << "x" << n << '\n';
        cout << "MPI processes: " << process_count << '\n';

        cout << fixed << setprecision(3);

        cout << "Sequential time: "
             << sequential_time << " ms\n";

        cout << "Parallel time: "
             << parallel_time * 1000.0 << " ms\n";

        cout << "Results saved to C.txt\n";

        if (parallel_time > 0.0)
        {
            cout << "Speedup: "
                 << sequential_time / (parallel_time * 1000.0)
                 << "x\n";
        }
    }

    MPI_Finalize();

    return 0;
}

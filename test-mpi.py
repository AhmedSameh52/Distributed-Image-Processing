from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
print('hello')
if rank == 0:
    data = {'a': 7, 'b': 3.14}
    for dest in range(1, comm.Get_size()):
        comm.send(data, dest=dest)
        print(f"sent data to Rank {dest}: {data}")
else:
    data = comm.recv(source=0)
    print(f"Received data on Rank {rank}: {data}")
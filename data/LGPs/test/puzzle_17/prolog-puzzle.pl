all_members([H], L) :- member(H, L).
all_members([H|T], L) :- member(H, L), all_members(T, L).

all_not_members([H], L) :- not(member(H, L)).
all_not_members([H|T], L) :- not(member(H, L)), all_not_members(T, L).

and([H]) :- H.
and([H|T]) :- H, and(T).

or([H]) :- H, !.
or([H|_]) :- H, !.
or([_|T]) :- or(T).

solve(B0,B1,B2,B3) :-
B0 = [A0, C0],
B1 = [A1, C1],
B2 = [A2, C2],
B3 = [A3, C3],

All = [B0,B1,B2,B3],

all_members([c0, c1, c2, c3], [C0, C1, C2, C3]),
all_members([50, 75, 100, 125], [A0, A1, A2, A3]),
or([and([C1 = c0,A2 = 100]),and([C2 = c0,A1 = 100])]),
A2-A0=:=25,
or([and([A2 = 75,member([100, c1], All)]),and([member([75, c1], All),A2 = 100])]),
and([or([A0 = 50,C0 = c2]), not(and([A0 = 50,C0 = c2]))]).

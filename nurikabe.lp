%
% Authors: SelinEsra (2017)
%

#const limit=5.

xcoo(1..limit).
ycoo(1..limit).

% white and black cells
color(w;b).

% generate the NxN grid
% field to show, visualization
% every field has x and y coordinates
field(f(X,Y)) :- xcoo(X), ycoo(Y).

% inputs
% initially all grid cells are white and some of them are numbered
numbered(f(1,1),4). 
numbered(f(1,3),1). 
numbered(f(1,5),1). 
numbered(f(3,3),2).
numbered(f(4,5),1). 
numbered(f(5,3),1). 

% for visualization
text(XX,N) :- numbered(XX,N).

% white cells that numbered field and its neighbors(paint the rest black/wall(python))
{cell(w,f(X,Y))} :- xcoo(X), ycoo(Y).
cell(b,f(X,Y)) :- not cell(w,f(X,Y)), xcoo(X), ycoo(Y).

% numbered cells remain white.
:- cell(b,C1), numbered(C1,N).

% every white cell is orthogonally connected to some numbered cell.
w_connected(C1) :-  connected(w,C1,C2), cell(w,C1), numbered(C2,N).
:- cell(w,C1), not w_connected(C1).

yadjacent(f(X,Y),f(X,Y+1)) :- xcoo(X), ycoo(Y), ycoo(Y+1).
xadjacent(f(X,Y),f(X+1,Y)) :- xcoo(X), ycoo(Y), xcoo(X+1).
yadjacent(A,B) :- yadjacent(B,A).
xadjacent(A,B) :- xadjacent(B,A).

adj(f(C,R),f(C1,R1)) :- xadjacent(f(C,R),f(C1,R1)).
adj(f(C,R),f(C1,R1)) :- yadjacent(f(C,R),f(C1,R1)).

connected(C,C1,C1) :- cell(C,C1), color(C).
connected(C,C1,C2) :- connected(C,C1,C3), adj(C3,C2), cell(C,C2), color(C).

% two numbered cells can not be orthogonally connected.
:- numbered(f(X,Y),N), numbered(f(U,V),M), X<U, connected(w,f(X,Y),f(U,V)).
:- numbered(f(X,Y),N), numbered(f(U,V),M), Y<V, connected(w,f(X,Y),f(U,V)).

% each numbered cell is an island cell, the number in it is the number of cells in that island.
island(C1) :- N {connected(w,C1,C2):xcoo(U),ycoo(V)} N, numbered(C1,N).
:- not island(C1), numbered(C1,N).

% all black cells should be connected orthogonally
:- not connected(b,C1,C2), cell(b,C1), cell(b,C2).

% there must be only one sea, which is not allowed to contain pools, 2x2 areas of black cells or larger.
:- sqrBlack(X,Y), xcoo(X), ycoo(Y).
sqrBlack(X,Y) :- cell(b,f(X+1,Y)), cell(b,f(X,Y)), cell(b,f(X, Y+1)), cell(b,f(X+1, Y+1)), xcoo(X), ycoo(Y).


% wall to show, visualization
wall(C1) :- cell(b,C1).












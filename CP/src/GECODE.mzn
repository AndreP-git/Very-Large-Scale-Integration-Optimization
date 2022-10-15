% Include
include "globals.mzn";

% Input parameters
int: max_width;
int: n_blocks;
set of int: blocks = 1..n_blocks;
array[blocks] of int: width;
array[blocks] of int: height;

% Checking parameters
% output["\(max_width)\n\(n_blocks)\n"] ++
%  ["\(width)\n\(height)\n"];

int: h = sum(height);
int: w = sum(width);

array[blocks] of var 0..w: cornerx;
array[blocks] of var 0..h: cornery;

% Constraints
% 0) each rectangle must be within max_width
constraint forall(b in blocks) (cornerx[b] + width[b] <= max_width);

% 1) defining boundaries for the resulting variable
var int: result = max(b in blocks)(cornery[b] + height[b]);
var int: min_height = ceil((sum(b in blocks)(width[b] * height[b]) div max_width));

constraint result >= max(max(height), min_height);
constraint forall(b in blocks) (cornery[b] + height[b] <= result);

% 1.5) non overlap (naive version)
constraint forall (b1 ,b2 in blocks where b1 < b2)
 (cornery [b1] + height [b1] <= cornery [b2] \/ 
 cornery [b2] + height [b2] <= cornery [b1 ] \/
 cornerx [b1] + width [b1] <= cornerx [b2] \/ 
 cornerx [b2] + width [b2] <= cornerx [b1]);

% 2) width constraints (keep these?? To speedup the search???)
array[blocks] of var bool: R;
constraint forall(b in blocks)(R[b] <-> width[b] > max_width / 2);
constraint forall(b in blocks)(
  if R[b]
  then cornerx[b] = 0
  endif
);

% 3) global constraints
constraint diffn(cornerx, cornery, width, height);
constraint cumulative(cornery, height, width, max_width);
constraint cumulative(cornerx, width, height, result);

% 4) simmetry breaking contraints
constraint forall(b1,b2 in blocks where
b1 < b2 /\
cornerx[b1]=cornerx[b2] /\ 
cornery[b1]+height[b1]=cornery[b2] /\
width[b1]=width[b2])
(lex_less([cornery[b1]],[cornery[b2]]));

constraint forall(b1,b2 in blocks where
b1 < b2 /\
cornery[b1]=cornery[b2] /\ 
cornerx[b1]+width[b1]=cornerx[b2] /\
height[b1]=height[b2])
(lex_less([cornerx[b1]],[cornerx[b2]]));

constraint forall(b1,b2 in blocks where
b1 < b2 /\
height[b1]=height[b2] /\
width[b1]=width[b2])
(lex_less([cornerx[b1],cornery[b1]], [cornerx[b2],cornery[b2]]));

% solving
%solve minimize result;

solve :: seq_search([
        int_search([result], smallest, indomain_min) :: restart_luby(200),
        int_search(cornerx, first_fail, indomain_min),
        int_search(cornery, first_fail, indomain_min)])
        minimize result;

% output
output["\(max_width) \(result)\n"] ++
  ["\(n_blocks)\n"] ++
  ["\(width[b]) \(height[b]) \(cornerx[b]) \(cornery[b])\n" | b in           blocks];


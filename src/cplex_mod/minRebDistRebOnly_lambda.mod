/*********************************************
 * minRebDistRebOnly.mod
 * 
 * Modified: 2025-12-04
 * Added: Slack variables (shortage) for soft constraints
 * 
 * PURPOSE:
 * Allow flexible rebalancing when costs are too high
 * by relaxing the "desired distribution" constraint.
 * 
 * HOW IT WORKS:
 * - shortage[i] = amount region i falls below desired target
 * - Objective: min(reb_cost + penalty * shortage)
 * - LP balances: cost vs target achievement
 * 
 * PARAMETERS:
 * - shortage_penalty: Higher = stricter target enforcement
 *   - Low (0.5-2): Prefers low cost, accepts more shortage
 *   - Medium (5-10): Balanced trade-off  
 *   - High (20+): Strongly enforces targets
 *********************************************/
tuple Edge{
  int i;
  int j;
}

tuple edgeAttrTuple{
    int i;
    int j;
    int t;
}

tuple accTuple{
  int i;
  float n;
}

string path = ...;

{edgeAttrTuple} edgeAttr = ...;
{accTuple} accInitTuple = ...;
{accTuple} accRLTuple = ...;

{Edge} edge = {<i,j>|<i,j,t> in edgeAttr};
{int} region = {i|<i,v> in accInitTuple};

float time[edge] = [<i,j>:t|<i,j,t> in edgeAttr];
float desiredVehicles[region] = [i:v|<i,v> in accRLTuple];
float vehicles[region] = [i:v|<i,v> in accInitTuple];

// Decision variables
dvar int+ rebFlow[edge];

// Slack variables for soft constraint
dvar float+ shortage[region];

// Penalty weight for shortage (adjust this to tune behavior)
float shortage_penalty = 1000.0;

// Objective: Minimize rebalancing cost + shortage penalty
minimize(
  sum(e in edge) (rebFlow[e]*time[e])        // Rebalancing cost
  + shortage_penalty * sum(i in region) shortage[i]  // Penalty for unmet targets
);

subject to
{
  forall(i in region)
    {
      // SOFT CONSTRAINT: Allow shortage
      // Original (HARD): sum(...) >= desiredVehicles[i] - vehicles[i]
      // Modified (SOFT): sum(...) + shortage[i] >= desired - vehicles
      // → LP can leave shortage > 0 if rebalancing is too expensive
      //ctDemand[i]:
      sum(e in edge: e.i==i && e.i!=e.j) (rebFlow[<e.j, e.i>] - rebFlow[<e.i, e.j>]) + shortage[i] >= desiredVehicles[i] - vehicles[i];

      // Vehicle capacity constraint (HARD - cannot violate)
      //ctCapacity[i]:
      sum(e in edge: e.i==i && e.i!=e.j) rebFlow[<e.i, e.j>] <= vehicles[i];
    }
}

main {
  thisOplModel.generate();
  cplex.solve();
  var ofile = new IloOplOutputFile(thisOplModel.path);
  var objValue = cplex.getObjValue();
  ofile.writeln("ObjectiveValue = " + objValue + ";");

  ofile.write("flow=[")
  for(var e in thisOplModel.edge)
       {
         ofile.write("(");
         ofile.write(e.i);
         ofile.write(",");
         ofile.write(e.j);
         ofile.write(",");
         ofile.write(thisOplModel.rebFlow[e]);
         ofile.write(")");
       }
  ofile.writeln("];")
  
  // Output shortage for debugging
  ofile.write("shortage=[")
  for(var i in thisOplModel.region)
       {
         ofile.write("(");
         ofile.write(i);
         ofile.write(",");
         ofile.write(thisOplModel.shortage[i]);
         ofile.write(")");
       }
  ofile.writeln("];");

  //shadow price 출력
  /*
  ofile.write("shadow_prices=[");
  for(var i in thisOplModel.region) {
    ofile.write("(");
    ofile.write(i);
    ofile.write(",");
    ofile.write(Math.abs(cplex.getReducedCost(thisOp  .shortage[i])));
    ofile.write(")");
  }
  ofile.writeln("];");
  */
  ofile.close();
}
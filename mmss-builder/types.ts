// Type definitions matching the MMSS Universal JSON Template

export interface MMSSMeta {
  system_id: string;
  description: string;
  domain_agnostic: boolean;
}

export interface StateVariable {
  description: string;
  examples: string[];
  dimension: string;
  symbolic_form: string;
}

export interface StateSpaceDynamics {
  state_equation: string;
  output_equation: string;
  F_type: string;
  G_type: string;
}

export interface StateSpace {
  X: StateVariable;
  U: StateVariable;
  Y: StateVariable;
  P: Pick<StateVariable, 'description' | 'examples' | 'symbolic_form'>;
  dynamics: StateSpaceDynamics;
}

export interface Storage {
  name: string;
  type: string;
  balance_equation: string;
}

export interface ParallelFlows {
  generic_split: string;
  branch_definition: string;
  usage: string;
}

export interface FlowsAndBalances {
  storages: Storage[];
  parallel_flows: ParallelFlows;
}

export interface Geometry {
  type: string;
  parameters: string[];
}

export interface RoleOfForm {
  performance_relation: string;
  notes: string;
}

export interface StructureAndForm {
  geometry: Geometry;
  role_of_form: RoleOfForm;
}

export interface BalanceOnEdge {
  definition: string;
  condition: string;
  examples: string[];
}

export interface Processes {
  types: string[];
  generic_operator: string;
}

export interface FeedbackLoop {
  name: string;
  type: string;
  purpose: string;
}

export interface ControlsAndFeedback {
  feedback_loops: FeedbackLoop[];
  control_law: string;
}

export interface MetaOptimization {
  objective_function: string;
  problem_form: string;
  methods: string[];
}

export interface FormalizationInstructions {
  step_1: string;
  step_2: string;
  step_3: string;
  step_4: string;
  step_5: string;
  step_6: string;
  step_7: string;
}

export interface MMSSUniversalTemplate {
  meta: MMSSMeta;
  STATE_SPACE: StateSpace;
  FLOWS_AND_BALANCES: FlowsAndBalances;
  STRUCTURE_AND_FORM: StructureAndForm;
  BALANCE_ON_EDGE: BalanceOnEdge;
  PROCESSES: Processes;
  CONTROLS_AND_FEEDBACK: ControlsAndFeedback;
  META_OPTIMIZATION: MetaOptimization;
  FORMALIZATION_INSTRUCTIONS: FormalizationInstructions;
}

export interface MMSSRoot {
  MMSS_UNIVERSAL_TEMPLATE: MMSSUniversalTemplate;
}

export enum AIProvider {
  GEMINI = 'GEMINI',
  MISTRAL = 'MISTRAL'
}

export interface AppState {
  inputText: string;
  jsonOutput: MMSSRoot | null;
  isLoading: boolean;
  error: string | null;
  provider: AIProvider;
  geminiKey: string;
  mistralKey: string;
}